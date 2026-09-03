import re
from datetime import date
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from rapidfuzz import fuzz

from app.core.time import parse_relative_date_range

# Common spelling mistakes and domain aliases
TYPO_AND_ALIAS_MAP: Dict[str, str] = {
    # Gen AI & AI
    "gen ai": "generative ai",
    "genai": "generative ai",
    "genarative ai": "generative ai",
    "generativ ai": "generative ai",
    "genrative ai": "generative ai",
    "generative ai": "generative ai",
    "generative artificial intelligence": "generative ai",
    # Categories & events
    "hackaton": "hackathon",
    "hackathn": "hackathon",
    "hackathons": "hackathon",
    "workshp": "workshop",
    "workshps": "workshop",
    "iot worshop": "iot workshop",
    "iot workshp": "iot workshop",
    "seminar": "seminar",
    "competishon": "competition",
    "competitions": "competition",
    "bootcamp": "bootcamp",
    "ideathon": "ideathon",
    # Relative dates
    "tomorow": "tomorrow",
    "tommorow": "tomorrow",
    "tomrw": "tomorrow",
    "todai": "today",
    "upcomming": "upcoming",
    "upcomin": "upcoming",
    # Event terms
    "regestration": "registration",
    "registraion": "registration",
    "regester": "register",
    "venu": "venue",
    "whr": "where",
    "whr is": "where is",
    "elgibility": "eligibility",
    "eligiblity": "eligibility",
    "schedul": "schedule",
    "timin": "timing",
    "timings": "timing",
}

# Known event catalog for entity matching
KNOWN_EVENTS = [
    {
        "id": "hackverse-2026",
        "title": "HackVerse 2026",
        "aliases": ["hackverse", "hackvers", "hack verse", "hackverse2026", "hackathon 2026"]
    },
    {
        "id": "iot-robotics-workshop",
        "title": "Hands-on IoT & Embedded Systems Workshop",
        "aliases": ["iot workshop", "iot robotics", "embedded systems", "embedded systems workshop", "riot club workshop", "iot embedded", "iot embedded systems", "robotics workshop"]
    },
    {
        "id": "ai-agents-bootcamp",
        "title": "Autonomous AI Agents & GenAI Bootcamp",
        "aliases": ["gen ai", "genai", "generative ai", "gen ai bootcamp", "generative ai workshop", "ai agents", "ai bootcamp", "generative ai bootcamp", "autonomous ai"]
    },
    {
        "id": "cybershield-ctf",
        "title": "CyberShield Capture The Flag (CTF)",
        "aliases": ["cybershield", "ctf", "cybershield ctf", "cyber security ctf", "null byte ctf", "cyber security challenge"]
    },
]


class QueryAnalysis(BaseModel):
    """Structured interpretation of user query for precision-first retrieval."""
    original_query: str
    normalized_query: str
    intent: str = Field(default="FIND_EVENTS", description="Intent: 'SPECIFIC_EVENT', 'TOPIC_SEARCH', 'DATE_SEARCH', 'CATEGORY_SEARCH', 'GENERAL_DISCOVERY'")
    entities: List[str] = Field(default_factory=list, description="Matched event titles or external IDs")
    matched_event_id: Optional[str] = None
    matched_event_title: Optional[str] = None
    topics: List[str] = Field(default_factory=list, description="Normalized topics e.g. 'generative ai', 'iot', 'cybersecurity'")
    category_filter: Optional[str] = None
    date_start: Optional[date] = None
    date_end: Optional[date] = None
    date_label: Optional[str] = None
    wants_related: bool = False
    wants_multiple: bool = False
    requested_count: Optional[int] = None


class QueryAnalyzer:
    """Performs typo correction, entity recognition, and intent extraction."""

    def normalize_typos(self, text: str) -> str:
        """Replace known spelling errors and domain aliases while preserving overall structure."""
        cleaned = text.strip().lower()

        # Replace multi-word aliases first, sorted by length descending
        for alias, target in sorted(TYPO_AND_ALIAS_MAP.items(), key=lambda x: -len(x[0])):
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, cleaned):
                cleaned = re.sub(pattern, target, cleaned)

        return cleaned

    def analyze(self, query: str) -> QueryAnalysis:
        original = query.strip()
        normalized = self.normalize_typos(original)
        clean_words_only = re.sub(r"[^\w\s]", " ", normalized).strip()

        # 1. Parse relative dates (e.g. today, tomorrow, this week)
        date_start, date_end, date_label = parse_relative_date_range(normalized)

        # 2. Extract requested count or intent for multiple
        wants_multiple = False
        requested_count = None
        if re.search(r"\b(all|list|show all|more|every|what events|upcoming events)\b", normalized):
            wants_multiple = True

        count_match = re.search(r"\b(\d+)\s+(events|workshops|hackathons)\b", normalized)
        if count_match:
            requested_count = int(count_match.group(1))
            wants_multiple = True

        # Check for related / similar queries
        wants_related = bool(re.search(r"\b(related|similar|other|like this|more like)\b", normalized))

        # 3. Category Detection
        category_filter = None
        if re.search(r"\bhackathons?\b", normalized):
            category_filter = "Hackathon"
        elif re.search(r"\bworkshops?\b", normalized):
            category_filter = "Workshop"
        elif re.search(r"\bseminars?\b", normalized):
            category_filter = "Seminar"
        elif re.search(r"\b(competitions?|ctf)\b", normalized):
            category_filter = "Competition"

        # 4. Specific Topic Detection (CRITICAL: Distinguish Gen AI from generic AI or HackVerse)
        topics: List[str] = []
        if re.search(r"\b(generative ai|gen ai|genai|ai agents)\b", normalized):
            topics.append("generative ai")
        elif re.search(r"\b(artificial intelligence|\bai\b)\b", normalized):
            topics.append("ai")

        if re.search(r"\b(internet of things|iot|embedded|esp32|microcontroller|robotics)\b", normalized):
            topics.append("iot")

        if re.search(r"\b(cybersecurity|security|ctf|capture the flag|hacking|infosec)\b", normalized):
            topics.append("cybersecurity")

        # 5. Entity & Title Matching with Typo / Fuzzy tolerance
        matched_event_id = None
        matched_event_title = None
        entities: List[str] = []

        best_score = 0.0
        best_event = None

        for event in KNOWN_EVENTS:
            title_lower = event["title"].lower()
            if title_lower in clean_words_only or clean_words_only in title_lower:
                score = 100.0
                if score > best_score:
                    best_score = score
                    best_event = event
                continue

            # Check aliases using regex word boundary
            for alias in event["aliases"]:
                if re.search(r"\b" + re.escape(alias) + r"\b", clean_words_only):
                    score = 98.0
                    if score > best_score:
                        best_score = score
                        best_event = event
                    break

                # Fuzzy token set ratio
                ratio = fuzz.token_set_ratio(alias, clean_words_only)
                if ratio >= 80 and ratio > best_score:
                    best_score = ratio
                    best_event = event

        # Direct fuzzy check against title
        if not best_event or best_score < 80:
            for event in KNOWN_EVENTS:
                ratio = fuzz.partial_ratio(event["title"].lower(), clean_words_only)
                if ratio >= 80 and ratio > best_score:
                    best_score = ratio
                    best_event = event

        # Topic fallback mapping if specific topic uniquely maps to an event
        if not best_event:
            if "generative ai" in topics and not wants_related:
                best_event = next((e for e in KNOWN_EVENTS if e["id"] == "ai-agents-bootcamp"), None)
            elif "iot" in topics and any(k in normalized for k in ["workshop", "embedded", "robotics"]):
                best_event = next((e for e in KNOWN_EVENTS if e["id"] == "iot-robotics-workshop"), None)
            elif "cybersecurity" in topics or "ctf" in normalized:
                best_event = next((e for e in KNOWN_EVENTS if e["id"] == "cybershield-ctf"), None)

        if best_event:
            matched_event_id = best_event["id"]
            matched_event_title = best_event["title"]
            entities.append(best_event["title"])

        # Determine overall intent
        intent = "GENERAL_DISCOVERY"
        if matched_event_id and not wants_related:
            intent = "SPECIFIC_EVENT"
        elif topics:
            intent = "TOPIC_SEARCH"
        elif date_label:
            intent = "DATE_SEARCH"
        elif category_filter:
            intent = "CATEGORY_SEARCH"

        return QueryAnalysis(
            original_query=original,
            normalized_query=normalized,
            intent=intent,
            entities=entities,
            matched_event_id=matched_event_id,
            matched_event_title=matched_event_title,
            topics=topics,
            category_filter=category_filter,
            date_start=date_start,
            date_end=date_end,
            date_label=date_label,
            wants_related=wants_related,
            wants_multiple=wants_multiple,
            requested_count=requested_count,
        )


query_analyzer = QueryAnalyzer()
