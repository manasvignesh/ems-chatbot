import re
from typing import Optional, Tuple

PRELOADED_RESPONSES = {
    "greeting_morning": "Good morning! 👋 How can I help you with today's or upcoming EMS events?",
    "greeting_afternoon": "Good afternoon! 👋 How can I help you with EMS events and workshops?",
    "greeting_evening": "Good evening! 👋 Looking for an event or need information about one?",
    "greeting_general": "Hey! 👋 I'm the EMS Assistant. Ask me about events, workshops, hackathons, schedules, venues, registrations, or anything related to EMS.",
    "thanks": "You're welcome! Let me know if you need anything else about EMS events. 😊",
    "bye": "See you! 👋 Hope you have a great time attending your events.",
    "identity": "I'm the official EMS Assistant for MLRIT CIE. I can help you discover events, check schedules and venues, understand registration details, team sizes, and official rules.",
    "capabilities": "I can help you:\n• Discover upcoming workshops, hackathons, seminars, and competitions\n• Check dates, start/end times, and campus venues\n• Understand registration deadlines, fees, eligibility, and team sizes\n• Look up official rules and preparation requirements",
    "help": "You can ask me things like:\n• *What events are happening today?*\n• *Any workshops this week?*\n• *Tell me about HackVerse.*\n• *Where is the IoT workshop?*\n• *What's the registration deadline?*",
}


def check_smalltalk_and_respond(message: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a message is purely a basic conversational message.
    Returns (is_pure_smalltalk, preloaded_response).
    If the message contains both greeting/smalltalk AND an actual EMS query (e.g. 'hello, what events are today?'),
    returns (False, None) so it proceeds through the full RAG pipeline.
    """
    clean = message.strip().lower()
    # Strip common trailing punctuation
    clean = re.sub(r"[?!.,]+$", "", clean).strip()

    # Check for meaningful EMS query indicators
    ems_query_indicators = [
        r"\b(event|events|hackathon|workshop|seminar|competition|ctf|bootcamp|fest)\b",
        r"\b(today|tomorrow|this week|next week|this month|weekend|schedule|timing|date)\b",
        r"\b(venue|where|location|room|lab|auditorium)\b",
        r"\b(register|registration|deadline|fee|eligibility|team|team size|prize|rules)\b",
        r"\b(hackverse|iot|gen\s*ai|generative|ai|robotics|cybersecurity)\b",
    ]

    has_real_query = any(re.search(pattern, clean) for pattern in ems_query_indicators)
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
