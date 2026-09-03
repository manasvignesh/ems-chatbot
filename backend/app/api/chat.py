import time
import uuid
import random
from typing import Dict, List, Optional, Union
from fastapi import APIRouter, HTTPException, Request, status
from app.models.chat import (
    ChatRequest,
    ChatResponseSuccess,
    ChatResponseOutOfScope,
    ChatResponseError,
    EventCard,
    SourceReference,
)
from app.ai.classifier import scope_classifier
from app.ai.query_analysis import query_analyzer
from app.ai.smalltalk import check_smalltalk_and_respond
from app.ai.faq_matcher import faq_matcher
from app.ai.gemini import gemini_client
from app.ai.prompts import build_guarded_prompt
from app.rag.hybrid_search import hybrid_search_engine
from app.services.conversation import conversation_manager
from app.core.config import settings
from app.core.logging import logger
from app.core.time import get_current_time

router = APIRouter()


def sanitize_text(text: str, max_chars: int = settings.MAX_MESSAGE_CHAR_LENGTH) -> str:
    """Sanitize user input string."""
    if not text:
        return ""
    clean = "".join(ch for ch in text if ch.isprintable() or ch in "\n\r\t")
    return clean.strip()[:max_chars]


# Simple token bucket in-memory rate limiter per IP / session
class SimpleRateLimiter:
    def __init__(self, limit_per_min: int = settings.RATE_LIMIT_REQUESTS_PER_MINUTE):
        self.limit = limit_per_min
        self.requests: Dict[str, List[float]] = {}

    def is_rate_limited(self, key: str) -> bool:
        now = time.time()
        window_start = now - 60.0
        reqs = self.requests.get(key, [])
        valid_reqs = [t for t in reqs if t > window_start]
        self.requests[key] = valid_reqs
        if len(valid_reqs) >= self.limit:
            return True
        self.requests[key].append(now)
        return False

rate_limiter = SimpleRateLimiter()

# Track Gemini avoidance metrics
USAGE_METRICS = {
    "total_queries": 0,
    "small_talk_queries": 0,
    "faq_exact_queries": 0,
    "faq_fuzzy_queries": 0,
    "faq_semantic_queries": 0,
    "rag_direct_queries": 0,
    "gemini_queries": 0,
    "out_of_scope_queries": 0,
}


@router.get("/config/{bot_id}")
async def get_bot_config(bot_id: str):
    """Fetch initial bot configuration and branding."""
    return {
        "bot_id": bot_id,
        "name": "The Equinox 2.0 Assistant",
        "title": "The Equinox 2.0 Assistant",
        "subtitle": "MLRIT CIE E-Summit",
        "greeting": "Hi! I can help you discover The Equinox 2.0 sub-events, dates (30–31 Oct), venue at MLRIT, competitions, sponsorship tiers, and contacts.",
        "placeholder": "Ask about Equinox events, venue, sponsorship...",
        "suggested_prompts": [
            "What is Equinox 2.0?",
            "What events are there?",
            "When is Equinox?",
            "Tell me about IPL Auction",
            "Which event is for internships?",
            "What is Startup Poly?",
            "What is Pitch Deck?",
            "Who can I contact?"
        ],
        "cooldown_seconds": settings.OUT_OF_SCOPE_COOLDOWN_SECONDS,
    }


@router.get("/metrics")
async def get_usage_metrics():
    """Get Gemini avoidance metrics."""
    total = USAGE_METRICS["total_queries"]
    gemini = USAGE_METRICS["gemini_queries"]
    avoided = total - gemini
    avoidance_rate = (avoided / total * 100) if total > 0 else 100.0

    return {
        **USAGE_METRICS,
        "gemini_avoided_queries": avoided,
        "gemini_avoidance_rate_pct": round(avoidance_rate, 2),
    }


@router.post(
    "/chat",
    response_model=Union[ChatResponseSuccess, ChatResponseOutOfScope, ChatResponseError],
)
async def chat_endpoint(request: Request, payload: ChatRequest):
    """Core user-facing chat endpoint for The Equinox 2.0 Assistant."""
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    conversation_id = payload.conversation_id or str(uuid.uuid4())
    USAGE_METRICS["total_queries"] += 1

    # 1. Rate Limiting Check
    rate_limit_key = f"{client_ip}:{conversation_id}"
    if rate_limiter.is_rate_limited(rate_limit_key):
        logger.warning(f"Rate limit exceeded for {rate_limit_key}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please wait a moment before sending another message.",
        )

    # 2. Input Sanitization
    clean_message = sanitize_text(payload.message, max_chars=settings.MAX_MESSAGE_CHAR_LENGTH)
    if not clean_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # 3. Fast Preloaded Small-Talk Layer (0 ms, 0 API calls)
    is_small_talk, fast_response = check_smalltalk_and_respond(clean_message)
    if is_small_talk and fast_response:
        USAGE_METRICS["small_talk_queries"] += 1
        conversation_manager.add_message(conversation_id, "user", clean_message)
        conversation_manager.add_message(conversation_id, "assistant", fast_response)
        logger.info(f"[Answer Mode: SMALL_TALK] query='{clean_message}' ({ (time.time() - start_time)*1000:.1f}ms)")
        return ChatResponseSuccess(
            status="success",
            conversation_id=conversation_id,
            answer=fast_response,
            sources=[],
            cards=[],
        )

    # 4. Fast Deterministic Equinox FAQ Matcher (Bypasses Gemini)
    matched_faq, faq_mode, confidence = faq_matcher.match(clean_message)
    if matched_faq and confidence >= 0.78:
        if faq_mode == "FAQ_EXACT":
            USAGE_METRICS["faq_exact_queries"] += 1
        elif faq_mode == "FAQ_FUZZY":
            USAGE_METRICS["faq_fuzzy_queries"] += 1
        else:
            USAGE_METRICS["faq_semantic_queries"] += 1

        faq_answer = matched_faq["answer"]
        conversation_manager.add_message(conversation_id, "user", clean_message)
        conversation_manager.add_message(conversation_id, "assistant", faq_answer)

        # Build card if specific sub-event is referenced
        cards: List[EventCard] = []
        entities = matched_faq.get("entities", [])
        if entities and entities[0] != "The Equinox 2.0" and entities[0] not in ("Sponsorship", "Contact"):
            sub_id = entities[0].lower().replace(" ", "-")
            cards.append(
                EventCard(
                    event_id=sub_id,
                    title=entities[0],
                    date="30–31 October",
                    venue="MLR Institute of Technology, Hyderabad",
                    organizer="MLRIT CIE",
                    category="Sub-Event",
                    url=f"/events/{sub_id}"
                )
            )

        sources = [SourceReference(title="The Equinox 2.0 Master Knowledge", source_type="Equinox Brochure & Prospectus", url="/events/equinox-2.0")]

        logger.info(f"[Answer Mode: {faq_mode}] query='{clean_message}' -> matched_faq='{matched_faq['id']}' (confidence={confidence:.2f}, {(time.time() - start_time)*1000:.1f}ms)")
        return ChatResponseSuccess(
            status="success",
            conversation_id=conversation_id,
            answer=faq_answer,
            sources=sources,
            cards=cards,
        )

    # 5. Conversational History Sync
    if payload.conversation_history:
        for msg in payload.conversation_history[-settings.MAX_CONVERSATION_HISTORY_MESSAGES:]:
            conversation_manager.add_message(conversation_id, msg.role, msg.content)

    has_active_conv = len(conversation_manager.get_history(conversation_id)) > 0
    conversation_manager.add_message(conversation_id, "user", clean_message)

    # 6. Layered Scope & Guardrail Classification (5 Levels)
    scope_eval = await scope_classifier.classify(
        message=clean_message,
        page_context=payload.page_context,
        has_active_conversation=has_active_conv,
    )

    # Handle CLEARLY_OUT_OF_SCOPE and SUSPICIOUS
    if scope_eval.classification in ("CLEARLY_OUT_OF_SCOPE", "SUSPICIOUS"):
        USAGE_METRICS["out_of_scope_queries"] += 1
        ticket_id = f"EQX-PASS-{random.randint(1000, 9999)}"
        is_suspicious = scope_eval.classification == "SUSPICIOUS"

        logger.info(f"[Answer Mode: {scope_eval.classification}] query='{clean_message}' (reason: {scope_eval.reason})")
        return ChatResponseOutOfScope(
            status="out_of_scope",
            conversation_id=conversation_id,
            classification_level="SUSPICIOUS" if is_suspicious else "CLEARLY_OUT_OF_SCOPE",
            warning_type="suspicious_pass" if is_suspicious else "invalid_event_pass",
            ticket_number=ticket_id,
            cooldown_seconds=2 if is_suspicious else 3,
            reason=scope_eval.reason,
            message="This assistant is focused on The Equinox 2.0. Ask me about events, dates, sub-events, venue, sponsorship, or contacts."
        )

    # Handle AMBIGUOUS with gentle clarification prompt (NO warning)
    if scope_eval.classification == "AMBIGUOUS" and scope_eval.clarification_prompt:
        conversation_manager.add_message(conversation_id, "assistant", scope_eval.clarification_prompt)
        logger.info(f"[Answer Mode: AMBIGUOUS_CLARIFICATION] query='{clean_message}'")
        return ChatResponseSuccess(
            status="success",
            conversation_id=conversation_id,
            answer=scope_eval.clarification_prompt,
            sources=[],
            cards=[],
        )

    # 7. Query Understanding & Typo Normalization
    query_analysis = query_analyzer.analyze(clean_message)

    # 8. Resolve Query Context (Pronouns 'it', 'that event')
    resolved_query = conversation_manager.resolve_query_context(query_analysis.normalized_query, conversation_id)

    # 9. Precision-First Hybrid RAG Retrieval
    try:
        chunks, event_cards, source_refs = await hybrid_search_engine.search(
            query=resolved_query,
            bot_id=payload.bot_id,
            page_context=payload.page_context,
            query_analysis=query_analysis,
            top_k=settings.MAX_RETRIEVAL_CHUNKS,
        )

        retrieved_text = "\n\n---\n\n".join([c.get("content", "") for c in chunks])

        page_ctx_str = ""
        if payload.page_context and payload.page_context.event_id:
            page_ctx_str = f"User is viewing event: {payload.page_context.event_name or payload.page_context.event_id} (ID: {payload.page_context.event_id})"

        # 10. Guarded Prompt Construction
        current_dt = get_current_time()
        conv_summary = conversation_manager.format_history_for_prompt(conversation_id)
        guarded_prompt = build_guarded_prompt(
            user_message=clean_message,
            retrieved_context=retrieved_text,
            conversation_summary=conv_summary,
            page_context_str=page_ctx_str,
            current_dt=current_dt,
        )

        # 11. Gemini Generation (Only when local FAQ didn't match)
        USAGE_METRICS["gemini_queries"] += 1
        answer = await gemini_client.generate_response(prompt=guarded_prompt)
        conversation_manager.add_message(conversation_id, "assistant", answer)

        latency_ms = (time.time() - start_time) * 1000
        logger.info(f"[Answer Mode: RAG_GEMINI] query='{clean_message}' (latency={latency_ms:.1f}ms)")

        return ChatResponseSuccess(
            status="success",
            conversation_id=conversation_id,
            answer=answer,
            sources=source_refs,
            cards=event_cards,
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        return ChatResponseError(
            status="error",
            message="We encountered an issue retrieving Equinox 2.0 details. Please try again.",
        )
