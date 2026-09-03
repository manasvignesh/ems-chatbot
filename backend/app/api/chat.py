import time
import uuid
from typing import Union
from fastapi import APIRouter, HTTPException, Request, Response, status

from app.ai.classifier import scope_classifier
from app.ai.gemini import gemini_client
from app.ai.prompts import build_guarded_prompt
from app.ai.query_analysis import query_analyzer
from app.ai.smalltalk import check_smalltalk_and_respond
from app.core.config import settings
from app.core.logging import logger
from app.core.security import rate_limiter, sanitize_text
from app.core.time import get_current_time
from app.models.chat import (
    ChatRequest,
    ChatResponseError,
    ChatResponseOutOfScope,
    ChatResponseSuccess,
)
from app.rag.hybrid_search import hybrid_search_engine
from app.services.conversation import conversation_manager

router = APIRouter(tags=["Chat"])


@router.get("/config/{bot_id}")
async def get_bot_config(bot_id: str):
    """Return bot metadata and suggested questions for the widget."""
    return {
        "bot_id": bot_id,
        "name": "EMS Assistant",
        "title": "EMS Assistant",
        "subtitle": "Event Assistant",
        "greeting": "Hi! I can help you discover events, understand event details, schedules, venues, registration information, rules, and other EMS-related information.",
        "placeholder": "Ask about events, venues, rules...",
        "suggested_prompts": [
            "Events happening today",
            "What workshops are happening this week?",
            "Any hackathons this month?",
            "Tell me about HackVerse",
            "Registration deadlines",
            "How should I prepare for a hackathon?"
        ],
        "cooldown_seconds": settings.OUT_OF_SCOPE_COOLDOWN_SECONDS,
    }


@router.post(
    "/chat",
    response_model=Union[ChatResponseSuccess, ChatResponseOutOfScope, ChatResponseError],
)
async def chat_endpoint(request: Request, payload: ChatRequest):
    """Core user-facing chat endpoint for EMS Assistant."""
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    conversation_id = payload.conversation_id or str(uuid.uuid4())

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

    # 3. Fast Preloaded Small-Talk Check (0ms, bypasses RAG & Gemini for pure greetings/thanks/help)
    is_small_talk, fast_response = check_smalltalk_and_respond(clean_message)
    if is_small_talk and fast_response:
        conversation_manager.add_message(conversation_id, "user", clean_message)
        conversation_manager.add_message(conversation_id, "assistant", fast_response)
        logger.info(f"Handled via preloaded conversation layer in {(time.time() - start_time)*1000:.1f}ms for conv: {conversation_id}")
        return ChatResponseSuccess(
            status="success",
            conversation_id=conversation_id,
            answer=fast_response,
            sources=[],
            cards=[],
        )

    # 4. Conversational History Sync (if client supplied additional history)
    if payload.conversation_history:
        for msg in payload.conversation_history[-settings.MAX_CONVERSATION_HISTORY_MESSAGES:]:
            conversation_manager.add_message(conversation_id, msg.role, msg.content)

    has_active_conv = len(conversation_manager.get_history(conversation_id)) > 0
    conversation_manager.add_message(conversation_id, "user", clean_message)

    # 5. Layered Scope & Guardrail Classification
    scope_eval = await scope_classifier.classify(
        message=clean_message,
        page_context=payload.page_context,
        has_active_conversation=has_active_conv,
    )

    # 6. Handle Out of Scope
    if scope_eval.classification == "OUT_OF_SCOPE":
        logger.info(f"Out of scope rejected query: '{clean_message}' (reason: {scope_eval.reason})")
        return ChatResponseOutOfScope(
            status="out_of_scope",
            conversation_id=conversation_id,
            cooldown_seconds=settings.OUT_OF_SCOPE_COOLDOWN_SECONDS,
            reason=scope_eval.reason,
        )

    # 7. Query Understanding & Typo Normalization
    query_analysis = query_analyzer.analyze(clean_message)

    # 8. Resolve Query Context (e.g. Pronouns 'it', 'that event')
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

        # Page context string
        page_ctx_str = ""
        if payload.page_context and payload.page_context.event_id:
            page_ctx_str = f"User is viewing event: {payload.page_context.event_name or payload.page_context.event_id} (ID: {payload.page_context.event_id})"

        # 10. Guarded Prompt Construction with Authoritative Time Context
        current_dt = get_current_time()
        conv_summary = conversation_manager.format_history_for_prompt(conversation_id)
        guarded_prompt = build_guarded_prompt(
            user_message=clean_message,
            retrieved_context=retrieved_text,
            conversation_summary=conv_summary,
            page_context_str=page_ctx_str,
            current_dt=current_dt,
        )

        # 11. Gemini Generation
        answer = await gemini_client.generate_response(prompt=guarded_prompt)
        conversation_manager.add_message(conversation_id, "assistant", answer)

        latency_ms = (time.time() - start_time) * 1000
        logger.info(f"Chat response generated in {latency_ms:.1f}ms for conv: {conversation_id}")

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
            message="We encountered an issue processing your question. Please try again shortly.",
        )
