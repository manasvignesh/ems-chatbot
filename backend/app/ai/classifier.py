import re
from typing import List, Optional
from app.models.chat import PageContext, ScopeClassificationResult
from app.ai.guardrails import detect_prompt_injection
from app.ai.gemini import gemini_client
from app.ai.prompts import SCOPE_CLASSIFIER_PROMPT
from app.core.logging import logger

# Confidently in-scope keywords/patterns
IN_SCOPE_PATTERNS = [
    r"(?i)\b(event|events|hackathon|workshop|seminar|competition|fest|webinar|meetup|ideathon|coding contest)\b",
    r"(?i)\b(schedule|timeline|timing|venue|location|room|auditorium|lab|ground|date|today|tomorrow|this week|this month|weekend)\b",
    r"(?i)\b(register|registration|deadline|fee|fees|cost|ticket|eligibility|eligible|team|team size|members|prizes?|certificate)\b",
    r"(?i)\b(rules|rule|guidelines|requirements|what to bring|carry|laptop|prerequisites|how to prepare|preparation)\b",
    r"(?i)\b(organizer|club|department|cie|mlrit|coordinator|lead|volunteer|contact)\b",
    r"(?i)\b(hi|hello|hey|help|good morning|good afternoon|good evening|who are you|what can you do)\b",
    r"(?i)\b(iot|ai|ml|blockchain|cybersecurity|web dev|robotics|app dev|cloud)\b",  # Common tech tracks in events
]

# Confidently out-of-scope patterns
OUT_OF_SCOPE_PATTERNS = [
    r"(?i)\b(ipl|cricket|fifa|football|world cup|match score|who won|who is winning)\b",
    r"(?i)\b(stock|stocks|crypto|bitcoin|trading|share market|forex|investment advice)\b",
    r"(?i)\b(movie|cinema|actor|actress|bollywood|hollywood|netflix|song|celebrity|gossip)\b",
    r"(?i)\b(weather|temperature|rain|forecast|climate)\b",
    r"(?i)\b(president|prime minister|election|parliament|politics|bjp|congress|democrat|republican)\b",
    r"(?i)\b(write\s+.*?(assignment|homework|essay|thesis|paper)|solve\s+.*?(calculus|physics|chemistry|math|biology|problem|exam))\b",
    r"(?i)\b(malware|ransomware|keylogger|ddos|exploit|hack (instagram|facebook|bank|wifi))\b",
    r"(?i)\b(recipe|cook|food delivery|zomato|swiggy|restaurant recommendation)\b",
    r"(?i)\b(joke|riddle|poem about love|dating advice)\b",
]

COMPILED_IN_SCOPE = [re.compile(p) for p in IN_SCOPE_PATTERNS]
COMPILED_OUT_OF_SCOPE = [re.compile(p) for p in OUT_OF_SCOPE_PATTERNS]


class ScopeClassifier:
    """Layered scope classification pipeline."""

    async def classify(
        self,
        message: str,
        page_context: Optional[PageContext] = None,
        has_active_conversation: bool = False,
    ) -> ScopeClassificationResult:
        query = message.strip()

        # Step 1: Prompt Injection Check
        is_injection, _ = detect_prompt_injection(query)
        if is_injection:
            return ScopeClassificationResult(
                classification="OUT_OF_SCOPE",
                confidence=0.99,
                reason="Prompt injection or system extraction attempt."
            )

        # Step 2: Clear Rule-Based Out-of-Scope check
        for pattern in COMPILED_OUT_OF_SCOPE:
            if pattern.search(query):
                # Ensure it's not explicitly framed in an event context (e.g. "Is there an IPL cricket hackathon?")
                if not any(k in query.lower() for k in ["event", "hackathon", "workshop", "competition", "ems"]):
                    return ScopeClassificationResult(
                        classification="OUT_OF_SCOPE",
                        confidence=0.96,
                        reason="Query clearly matches unrelated general/entertainment/sports domains."
                    )

        # Step 3: Page Context Boost
        # If user is on an event detail page, follow-up queries like "What is the team size?", "Where is it?" are definitely in scope
        if page_context and page_context.event_id:
            logger.info(f"Classified query under active page context for event: {page_context.event_id}")
            return ScopeClassificationResult(
                classification="IN_SCOPE",
                confidence=0.95,
                reason="User is querying within active event detail page context."
            )

        # Step 4: Active Conversation Context Boost
        if has_active_conversation:
            # Short pronoun queries like "Where is it?", "When?", "Can 1st years join?"
            short_follow_ups = [
                r"(?i)^(where|when|what|who|how|why|is it|can i|can we|are there)\b",
                r"(?i)\b(it|this|that|second|first|third|next|more)\b",
            ]
            if any(re.search(p, query) for p in short_follow_ups) and len(query.split()) < 12:
                return ScopeClassificationResult(
                    classification="IN_SCOPE",
                    confidence=0.90,
                    reason="Conversational follow-up in active event session."
                )

        # Step 5: Clear Rule-Based In-Scope Check
        for pattern in COMPILED_IN_SCOPE:
            if pattern.search(query):
                return ScopeClassificationResult(
                    classification="IN_SCOPE",
                    confidence=0.92,
                    reason="Query matches known EMS and college event keywords."
                )

        # Step 6: Ambiguous / Unknown query -> Call Gemini JSON classifier
        logger.info(f"Ambiguous query '{query}', calling structured Gemini classifier...")
        try:
            classification_prompt = (
                f"Query: \"{query}\"\n"
                f"Page context: {page_context.model_dump_json() if page_context else 'None'}\n"
                f"Has conversation history: {has_active_conversation}\n"
            )
            result = await gemini_client.generate_structured_json(
                prompt=classification_prompt,
                system_instruction=SCOPE_CLASSIFIER_PROMPT,
            )

            classification = result.get("classification", "IN_SCOPE")
            confidence = float(result.get("confidence", 0.8))
            reason = result.get("reason", "Evaluated by AI classifier.")

            return ScopeClassificationResult(
                classification=classification,
                confidence=confidence,
                reason=reason
            )
        except Exception as e:
            logger.warning(f"Fallback classification due to AI classifier error: {e}")
            # If uncertain and not flagged out of scope, treat as IN_SCOPE with low confidence
            return ScopeClassificationResult(
                classification="IN_SCOPE",
                confidence=0.60,
                reason="Defaulted to in-scope on classifier fallback."
            )


scope_classifier = ScopeClassifier()
