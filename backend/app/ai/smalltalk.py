import re
from typing import Optional, Tuple

PRELOADED_RESPONSES = {
    "greeting_morning": "Good morning! 👋 How can I help you explore The Equinox 2.0 and its sub-events?",
    "greeting_afternoon": "Good afternoon! 👋 How can I assist you with The Equinox 2.0 at MLRIT?",
    "greeting_evening": "Good evening! 👋 Looking for events, competitions, or sponsorship details at The Equinox 2.0?",
    "greeting_general": "Hey! 👋 I'm the Equinox 2.0 Assistant. Ask me about sub-events, dates (30–31 Oct), venue at MLRIT, competitions, sponsorship packages, or contacts.",
    "thanks": "You're welcome! Let me know if you need anything else regarding The Equinox 2.0. 😊",
    "bye": "See you! 👋 Look forward to seeing you at The Equinox 2.0 on 30–31 October at MLRIT.",
    "identity": "I'm the official AI Assistant for The Equinox 2.0, the 2-day flagship E-Summit hosted by the Centre for Innovation & Entrepreneurship (CIE) at MLRIT Hyderabad.",
    "capabilities": "I can help you:\n• Discover the 10 sub-events (Spotlight, Crossroads, Startup Expo, Brand Battles, IPL Auction, Hustle Mania, Internship Drive, Startup Poly, E-Cell Meet, Pitch Deck)\n• Check event dates (30–31 October) and venue at MLRIT Hyderabad\n• Understand sponsorship tiers (Associate, Premium, Exclusive, Title)\n• Look up MLRIT-CIE details and student coordinator contact information",
    "help": "You can ask me things like:\n• *What is Equinox 2.0?*\n• *What events are there?*\n• *When is Equinox?*\n• *Tell me about IPL Auction.*\n• *Which event is like Monopoly?*\n• *Which event offers internships?*\n• *What sponsorship packages are available?*\n• *Who can I contact?*",
}


def check_smalltalk_and_respond(message: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a message is purely a basic conversational message.
    Returns (is_pure_smalltalk, preloaded_response).
    """
    clean = message.strip().lower()
    clean = re.sub(r"[?!.,]+$", "", clean).strip()

    # If the message contains specific Equinox or sub-event inquiry keywords, it's not pure small talk
    equinox_query_indicators = [
        r"\b(equinox|spotlight|crossroads|startup expo|brand battles|ipl auction|hustle mania|internship drive|startup poly|e-cell meet|pitch deck)\b",
        r"\b(date|dates|october|30|31|venue|location|where|address|hyderabad|mlrit|cie)\b",
        r"\b(sponsor|sponsorship|package|tier|price|cost|contact|email|phone|coordinators)\b",
        r"\b(monopoly|internship|internships|pitch|pitching|case study|brand debate|auction)\b",
    ]

    has_real_query = any(re.search(pattern, clean) for pattern in equinox_query_indicators)
    if has_real_query:
        return False, None

    # 1. Greetings
    if re.fullmatch(r"(good\s*morning|gud\s*morning|morning)", clean):
        return True, PRELOADED_RESPONSES["greeting_morning"]

    if re.fullmatch(r"(good\s*afternoon|afternoon)", clean):
        return True, PRELOADED_RESPONSES["greeting_afternoon"]

    if re.fullmatch(r"(good\s*evening|evening)", clean):
        return True, PRELOADED_RESPONSES["greeting_evening"]

    if re.fullmatch(r"(hi|hello|hey|hii|hiii|hiiii|heyy|heya|yo|hola|hello\s+there|hey\s+bot|hi\s+bot|hello\s+bot)", clean):
        return True, PRELOADED_RESPONSES["greeting_general"]

    # 2. Thanks / Gratitude
    if re.fullmatch(r"(thanks|thank\s*you|thanku|thank\s*u|thx|tysm|thanks\s+a\s+lot|thanks\s+bro|thank\s+you\s+so\s+much)", clean):
        return True, PRELOADED_RESPONSES["thanks"]

    # 3. Farewells
    if re.fullmatch(r"(bye|goodbye|good\s*bye|see\s*you|cya|take\s*care|bye\s*bye)", clean):
        return True, PRELOADED_RESPONSES["bye"]

    # 4. Identity
    if re.fullmatch(r"(who\s+are\s+you|what\s+are\s+you|your\s+name|what\s+is\s+your\s+name|tell\s+me\s+about\s+yourself)", clean):
        return True, PRELOADED_RESPONSES["identity"]

    # 5. Capabilities
    if re.fullmatch(r"(what\s+can\s+you\s+do|what\s+do\s+you\s+do|how\s+can\s+you\s+help(\s+me)?|features|capabilities)", clean):
        return True, PRELOADED_RESPONSES["capabilities"]

    # 6. Help
    if re.fullmatch(r"(help|help\s+me|how\s+to\s+use|guide|support)", clean):
        return True, PRELOADED_RESPONSES["help"]

    return False, None
