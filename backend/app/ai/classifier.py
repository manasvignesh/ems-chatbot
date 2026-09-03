import re
from typing import List, Optional
from app.models.chat import PageContext, ScopeClassificationResult
from app.ai.guardrails import detect_prompt_injection
from app.ai.gemini import gemini_client
from app.ai.prompts import SCOPE_CLASSIFIER_PROMPT
from app.core.logging import logger

# Explicitly named Equinox events, activities, and shorthands
EXPLICIT_EQUINOX_TERMS = [
    # Master event & CIE
    r"(?i)\b(equinox|the equinox|equinx|esummit|e-summit|summit|cie|mlrit|mlrit-cie|mlrit cie)\b",
    # 10 Official Sub-Events & Typos
    r"(?i)\b(spotlight|spotlite|crossroads|crossraods|startup expo|brand battles?|ipl auction|hustle mania|hustle maniya|internship drive|startup poly|startup polly|e-cell meet|pitch deck|pitchdek)\b",
    # Activity Shorthands
    r"(?i)\b(auction|bidding|player auction|cricket auction)\b",
    r"(?i)\b(pitch|pitching|startup pitch|investor pitch)\b",
    r"(?i)\b(monopoly|monopoly event|monopoly game)\b",
    r"(?i)\b(internship|internships|career drive)\b",
    r"(?i)\b(selling|selling competition|live marketing)\b",
    r"(?i)\b(business case|business case event|case study|business strategy)\b",
    r"(?i)\b(brand debate|brand fight|company debate)\b",
    r"(?i)\b(startup showcase|expo|exhibition)\b",
    r"(?i)\b(industry speaker event|industry speaker|speaker event|keynote|keynotes|speaker talks?|industry talks?|expert talks?|guest lecture)\b",
    r"(?i)\b(e-cell|ecell|e cell|student leaders?)\b",
    r"(?i)\b(sponsorship|sponsors|sponsor packages?|associate sponsor|title sponsor|premium sponsor|exclusive sponsor)\b",
    r"(?i)\b(coordinator|coordinators|shyam|sanjana|mahima|adithya)\b",
    r"(?i)\b(startup|startups|entrepreneurship|entrepreneur|founders?)\b",
    r"(?i)\b(who should i contact|where is it|when is it|equinox date|registration fee|ticket price)\b",
    r"(?i)\b(hi|hello|hey|help|good morning|good afternoon|good evening|who are you|what can you do)\b",
]

# Confidently out-of-scope patterns (Strictly unrelated external domains)
OUT_OF_SCOPE_PATTERNS = [
    # Real-world sports scores & cricket news (Intent-specific, distinct from simulated IPL auction)
    r"(?i)\b(who won (yesterday|the match|ipl)|match score|cricket score|live score|ipl score|points table|yesterday'?s? match|india vs australia score|cricket match score|fifa|football score|world cup|premier league|champions league|nba score)\b",
    # Crypto / stock market
    r"(?i)\b(stock|stocks|crypto|bitcoin|ethereum|trading|share market|forex|investment advice|stock price|stock market)\b",
    # Movies / Celebrity gossip
    r"(?i)\b(movie|movies|cinema|actor|actress|bollywood|hollywood|netflix recommendations?|song|songs|celebrity|gossip|celebrity news)\b",
    # Weather
    r"(?i)\b(weather|temperature|rain forecast|climate|weather today)\b",
    # Politics & World Leaders
    r"(?i)\b(president of usa|who is us president|who is president|prime minister|election results?|parliament|politics|bjp|congress|democrat|republican)\b",
    # Academic homework / Code writing
    r"(?i)\b(write\s+.*?(assignment|homework|essay|thesis|paper)|solve\s+.*?(calculus|physics|chemistry|math|biology|integral|derivative|exam))\b",
    r"(?i)\b(write\s+(a\s+)?(python|javascript|c\+\+|java|rust|sql|html|css|php)?\s*(script|code|function|program|app)|debug\s+my\s+code|build\s+me\s+a\s+website)\b",
    # Malicious
    r"(?i)\b(malware|ransomware|keylogger|ddos|exploit|hack (instagram|facebook|bank|wifi))\b",
    # Food recipes
    r"(?i)\b(recipe|cook|food delivery|zomato|swiggy|restaurant recommendation|recipe for)\b",
    # Dating / Jokes
    r"(?i)\b(tell me a joke|riddle|poem about love|dating advice)\b",
]

COMPILED_EXPLICIT_TERMS = [re.compile(p) for p in EXPLICIT_EQUINOX_TERMS]
COMPILED_OUT_OF_SCOPE = [re.compile(p) for p in OUT_OF_SCOPE_PATTERNS]


class ScopeClassifier:
    """Layered scope classification pipeline with conservative false-positive protection."""

    async def classify(
        self,
        message: str,
        page_context: Optional[PageContext] = None,
        has_active_conversation: bool = False,
    ) -> ScopeClassificationResult:
        query = message.strip()
        lower_q = query.lower()

        # Step 1: Prompt Injection Check -> CLEARLY_OUT_OF_SCOPE
        is_injection, _ = detect_prompt_injection(query)
        if is_injection:
            return ScopeClassificationResult(
                classification="CLEARLY_OUT_OF_SCOPE",
                confidence=0.99,
                reason="Prompt injection or system extraction attempt."
            )

        # Step 2: Check Clear Out-of-Scope Patterns FIRST
        for pattern in COMPILED_OUT_OF_SCOPE:
            if pattern.search(lower_q):
                return ScopeClassificationResult(
                    classification="CLEARLY_OUT_OF_SCOPE",
                    confidence=0.96,
                    reason="Query clearly matches unrelated general/entertainment/sports domains."
                )

        # Step 3: Explicit Equinox, Sub-Event, Activity & Shorthand Identifiers (IN_SCOPE)
        for pattern in COMPILED_EXPLICIT_TERMS:
            if pattern.search(lower_q):
                return ScopeClassificationResult(
                    classification="IN_SCOPE",
                    confidence=0.95,
                    reason="Query matches Equinox 2.0 sub-event, activity, or shorthand keyword."
                )

        # Step 4: Ambiguous single-word cricket queries (e.g. "cricket", "is cricket involved?")
        if re.search(r"(?i)\b(cricket|batting|bowling)\b", lower_q):
            return ScopeClassificationResult(
                classification="AMBIGUOUS",
                confidence=0.65,
                reason="Ambiguous cricket query. Likely refers to Equinox IPL Auction simulation.",
                clarification_prompt="Are you asking about the Equinox IPL Auction? It is an interactive simulated cricket auction where participants bid for players to build a team."
            )

        # Step 5: Page Context Boost
        if page_context and page_context.event_id:
            logger.info(f"Classified query under active page context for event: {page_context.event_id}")
            return ScopeClassificationResult(
                classification="IN_SCOPE",
                confidence=0.95,
                reason="User is querying within active event detail page context."
            )

        # Step 6: Active Conversation Context
        if has_active_conversation and len(query.split()) <= 4:
            return ScopeClassificationResult(
                classification="LIKELY_IN_SCOPE",
                confidence=0.75,
                reason="Short follow-up within active conversation."
            )

        # Step 7: Fallback to LLM Classifier if borderline/ambiguous
        logger.info(f"Evaluating borderline query '{query}' with AI scope classifier...")
        try:
            res_dict = await gemini_client.generate_structured_json(
                prompt=f"{SCOPE_CLASSIFIER_PROMPT}\n\nUser Message: {query}",
                system_instruction=SCOPE_CLASSIFIER_PROMPT
            )
            raw_cls = res_dict.get("classification", "AMBIGUOUS")
            conf = float(res_dict.get("confidence", 0.7))

            if raw_cls in ("IN_SCOPE", "LIKELY_IN_SCOPE"):
                final_cls = "IN_SCOPE" if conf >= 0.8 else "LIKELY_IN_SCOPE"
            elif raw_cls in ("OUT_OF_SCOPE", "CLEARLY_OUT_OF_SCOPE"):
                final_cls = "CLEARLY_OUT_OF_SCOPE" if conf >= 0.90 else "SUSPICIOUS"
            else:
                final_cls = "AMBIGUOUS"

            return ScopeClassificationResult(
                classification=final_cls,
                confidence=conf,
                reason=res_dict.get("reason", "Evaluated by AI scope classifier."),
                clarification_prompt=res_dict.get("clarification_prompt")
            )
        except Exception as e:
            logger.warning(f"AI classifier fallback failed: {e}. Defaulting conservatively to AMBIGUOUS.")
            return ScopeClassificationResult(
                classification="AMBIGUOUS",
                confidence=0.50,
                reason="Ambiguous query. Treating cautiously as potentially in scope."
            )


scope_classifier = ScopeClassifier()
