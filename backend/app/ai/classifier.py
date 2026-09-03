import re
from typing import List, Optional
from app.models.chat import PageContext, ScopeClassificationResult
from app.ai.guardrails import detect_prompt_injection
from app.ai.gemini import gemini_client
from app.ai.prompts import SCOPE_CLASSIFIER_PROMPT
from app.core.logging import logger

# Confidently in-scope keywords/patterns for The Equinox 2.0
IN_SCOPE_PATTERNS = [
    r"(?i)\b(equinox|the equinox|esummit|e-summit|summit)\b",
    r"(?i)\b(spotlight|crossroads|startup expo|brand battles|ipl auction|hustle mania|internship drive|startup poly|e-cell meet|pitch deck)\b",
    r"(?i)\b(event|events|sub-events|sub events|competition|competitions|expo|debate|auction|selling|internship|internships|monopoly|pitch|pitching|ecell|e-cell)\b",
    r"(?i)\b(schedule|timeline|timing|venue|location|room|auditorium|ground|date|dates|october|30|31|today|tomorrow|this week|this month|weekend)\b",
    r"(?i)\b(register|registration|deadline|fee|fees|cost|ticket|eligibility|eligible|team|team size|members|prizes?|certificate)\b",
    r"(?i)\b(sponsor|sponsors|sponsorship|packages?|tiers?|title sponsor|associate sponsor|premium sponsor|exclusive sponsor)\b",
    r"(?i)\b(organizer|club|department|cie|mlrit|mlrit-cie|coordinator|coordinators|shyam|sanjana|mahima|adithya|contact|email|phone)\b",
    r"(?i)\b(hi|hello|hey|help|good morning|good afternoon|good evening|who are you|what can you do)\b",
]

# Confidently out-of-scope patterns
OUT_OF_SCOPE_PATTERNS = [
    r"(?i)\b(who won (yesterday|the match|ipl)|match score|cricket score|live score|ipl score|points table|yesterday'?s? match)\b",
    r"(?i)\b(fifa|football|world cup|premier league|champions league|nba)\b",
    r"(?i)\b(stock|stocks|crypto|bitcoin|ethereum|trading|share market|forex|investment advice)\b",
    r"(?i)\b(movie|movies|cinema|actor|actress|bollywood|hollywood|netflix|song|songs|celebrity|gossip)\b",
    r"(?i)\b(weather|temperature|rain|forecast|climate)\b",
    r"(?i)\b(president|prime minister|election|parliament|politics|bjp|congress|democrat|republican)\b",
    r"(?i)\b(write\s+.*?(assignment|homework|essay|thesis|paper)|solve\s+.*?(calculus|physics|chemistry|math|biology|integral|derivative|exam))\b",
    r"(?i)\b(write\s+(a\s+)?(python|javascript|c\+\+|java|rust|sql|html|css|php)?\s*(script|code|function|program|app)|debug\s+my\s+code|build\s+me\s+a\s+website)\b",
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
        lower_q = query.lower()

        # Step 1: Prompt Injection Check
        is_injection, _ = detect_prompt_injection(query)
        if is_injection:
            return ScopeClassificationResult(
                classification="OUT_OF_SCOPE",
                confidence=0.99,
                reason="Prompt injection or system extraction attempt."
            )

        # Step 2: Clear Out-of-Scope check
        for pattern in COMPILED_OUT_OF_SCOPE:
            if pattern.search(query):
                return ScopeClassificationResult(
                    classification="OUT_OF_SCOPE",
                    confidence=0.96,
                    reason="Query clearly matches unrelated general/entertainment/sports domains."
                )

        # Step 3: Explicit Equinox In-Scope Patterns
        for pattern in COMPILED_IN_SCOPE:
            if pattern.search(query):
                return ScopeClassificationResult(
                    classification="IN_SCOPE",
                    confidence=0.95,
                    reason="Query matches Equinox 2.0 domain keywords."
                )

        # Step 4: Page Context Boost
        if page_context and page_context.event_id:
            logger.info(f"Classified query under active page context for event: {page_context.event_id}")
            return ScopeClassificationResult(
                classification="IN_SCOPE",
                confidence=0.95,
                reason="User is querying within active event detail page context."
            )

        # Step 5: Active Conversation context
        if has_active_conversation and len(query.split()) <= 4:
            return ScopeClassificationResult(
                classification="IN_SCOPE",
                confidence=0.80,
                reason="Short follow-up within active conversation."
            )

        # Step 6: Fallback to LLM Classifier if ambiguous
        logger.info(f"Ambiguous query '{query}', calling structured Gemini classifier...")
        try:
            res_dict = await gemini_client.generate_structured_json(
                prompt=f"{SCOPE_CLASSIFIER_PROMPT}\n\nUser Message: {query}"
            )
            return ScopeClassificationResult(
                classification=res_dict.get("classification", "OUT_OF_SCOPE"),
                confidence=float(res_dict.get("confidence", 0.7)),
                reason=res_dict.get("reason", "Evaluated by AI scope classifier.")
            )
        except Exception as e:
            logger.warning(f"AI classifier fallback failed: {e}. Defaulting to conservative OUT_OF_SCOPE.")
            return ScopeClassificationResult(
                classification="OUT_OF_SCOPE",
                confidence=0.60,
                reason="Ambiguous query outside of verified Equinox domain."
            )


scope_classifier = ScopeClassifier()
