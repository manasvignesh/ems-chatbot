import re
from datetime import date
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from rapidfuzz import fuzz

from app.core.time import parse_relative_date_range

# Common spelling mistakes and domain aliases for Equinox 2.0
TYPO_AND_ALIAS_MAP: Dict[str, str] = {
    # Equinox & CIE
    "equniox": "equinox",
    "equinx": "equinox",
    "equinoxx": "equinox",
    "e summit": "e-summit",
    "esummit": "e-summit",
    # Sub-events
    "spotlite": "spotlight",
    "cross road": "crossroads",
    "crossraods": "crossroads",
    "start up expo": "startup expo",
    "brand batles": "brand battles",
    "ipl action": "ipl auction",
    "ipl aucion": "ipl auction",
    "hustle maniya": "hustle mania",
    "intership drive": "internship drive",
    "internsip drive": "internship drive",
    "interships": "internships",
    "startup polly": "startup poly",
    "monopoly event": "startup poly",
    "monopoly game": "startup poly",
    "ecell meet": "e-cell meet",
    "e cell meet": "e-cell meet",
    "ecell": "e-cell",
    "pitchdeck": "pitch deck",
    "pitch idea": "pitch deck",
    "pitch to investors": "pitch deck",
    # Categories & terms
    "workshp": "workshop",
    "hackaton": "hackathon",
    "competishon": "competition",
    "sponser": "sponsor",
    "sponsership": "sponsorship",
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
    "tomorow": "tomorrow",
    "todai": "today",
    "upcomming": "upcoming",
}

# Equinox 2.0 and its 10 sub-events catalog for entity matching
KNOWN_EVENTS = [
    {
        "id": "equinox-2.0",
        "title": "The Equinox 2.0",
        "aliases": [
            "equinox", "the equinox", "equinox 2.0", "the equinox 2.0", "e-summit", "esummit",
            "mlrit equinox", "cie equinox", "summit"
        ]
    },
    {
        "id": "spotlight",
        "title": "Spotlight",
        "aliases": [
            "spotlight", "spotlite", "expert talks", "industry talks", "tech talks", "keynotes",
            "speaker sessions", "industry trends", "presentations"
        ]
    },
    {
        "id": "crossroads",
        "title": "Crossroads",
        "aliases": [
            "crossroads", "cross road", "crossraods", "case study", "business case study",
            "case study competition", "business challenges", "problem solving"
        ]
    },
    {
        "id": "startup-expo",
        "title": "Startup Expo",
        "aliases": [
            "startup expo", "start up expo", "expo", "startup showcase", "showcase startups",
            "product showcase", "startup stalls", "exhibition"
        ]
    },
    {
        "id": "brand-battles",
        "title": "Brand Battles",
        "aliases": [
            "brand battles", "brand batles", "brand debate", "rival brands", "brand wars",
            "brand strategy debate", "defend brands"
        ]
    },
    {
        "id": "ipl-auction",
        "title": "IPL Auction",
        "aliases": [
            "ipl auction", "ipl action", "ipl aucion", "cricket auction", "cricket bidding",
            "player bidding", "cricket simulation", "ipl simulation", "cricket auction event"
        ]
    },
    {
        "id": "hustle-mania",
        "title": "Hustle Mania",
        "aliases": [
            "hustle mania", "hustle maniya", "selling event", "sales competition",
            "marketing competition", "negotiation event", "sell products", "product selling"
        ]
    },
    {
        "id": "internship-drive",
        "title": "Internship Drive",
        "aliases": [
            "internship drive", "intership drive", "internsip drive", "internships", "internship",
            "hiring drive", "career drive", "internship opportunities"
        ]
    },
    {
        "id": "startup-poly",
        "title": "Startup Poly",
        "aliases": [
            "startup poly", "startup polly", "monopoly", "monopoly event", "monopoly game",
            "business simulation", "startup simulation", "board game"
        ]
    },
    {
        "id": "e-cell-meet",
        "title": "E-Cell Meet",
        "aliases": [
            "e-cell meet", "ecell meet", "e cell meet", "ecell", "e-cell", "e-cells",
            "cross campus collaboration", "e-cell networking"
        ]
    },
    {
        "id": "pitch-deck",
        "title": "Pitch Deck",
        "aliases": [
            "pitch deck", "pitchdeck", "startup pitching", "pitch idea", "pitch to investors",
            "pitching event", "present startup idea", "investor pitch"
        ]
    }
]


class QueryAnalysis(BaseModel):
    """Structured interpretation of user query for precision-first retrieval."""
    original_query: str
    normalized_query: str
    intent: str = Field(default="FIND_EVENTS", description="Intent: 'SPECIFIC_EVENT', 'TOPIC_SEARCH', 'DATE_SEARCH', 'SPONSORSHIP', 'CONTACT', 'GENERAL_DISCOVERY'")
    entities: List[str] = Field(default_factory=list, description="Matched event titles or external IDs")
    matched_event_id: Optional[str] = None
    matched_event_title: Optional[str] = None
    topics: List[str] = Field(default_factory=list, description="Normalized topics e.g. 'sponsorship', 'contact', 'sub_events', 'dates'")
    category_filter: Optional[str] = None
    date_start: Optional[date] = None
    date_end: Optional[date] = None
    date_label: Optional[str] = None
    wants_related: bool = False
    wants_multiple: bool = False
    requested_count: Optional[int] = None


class QueryAnalyzer:
    """Performs typo correction, entity recognition, and intent extraction for Equinox."""

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

        # 1. Relative date expressions
        date_start, date_end, date_label = parse_relative_date_range(normalized)

        # 2. Extract count / list intent
        wants_multiple = False
        requested_count = None
        if re.search(r"\b(all|list|all events|show all|give me all|sub events|activities)\b", normalized):
            wants_multiple = True

        count_match = re.search(r"\b(\d+)\s+(events|sub-events|activities)\b", normalized)
        if count_match:
            requested_count = int(count_match.group(1))
            wants_multiple = True

        wants_related = bool(re.search(r"\b(related|similar|other|like this)\b", normalized))

        # 3. Topic & Category Recognition
        topics: List[str] = []
        if re.search(r"\b(sponsor|sponsors|sponsorship|packages|tiers|title sponsor|associate sponsor|premium sponsor|exclusive sponsor)\b", normalized):
            topics.append("sponsorship")

        if re.search(r"\b(contact|email|phone|coordinator|coordinators|shyam|sanjana|mahima|adithya|reach out)\b", normalized):
            topics.append("contact")

        if re.search(r"\b(cie|mlrit cie|centre for innovation|incubation|cohorts|metaloop|inventron)\b", normalized):
            topics.append("cie")

        if re.search(r"\b(scale|footfall|participants|impressions|startups|numbers|metrics)\b", normalized):
            topics.append("impact")

        # 4. Match against Known Equinox Sub-Events
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

        if best_event:
            matched_event_id = best_event["id"]
            matched_event_title = best_event["title"]
            entities.append(best_event["title"])

        # Determine overall intent
        intent = "GENERAL_DISCOVERY"
        if matched_event_id and not wants_related:
            intent = "SPECIFIC_EVENT"
        elif "sponsorship" in topics:
            intent = "SPONSORSHIP"
        elif "contact" in topics:
            intent = "CONTACT"
        elif date_label:
            intent = "DATE_SEARCH"

        return QueryAnalysis(
            original_query=original,
            normalized_query=normalized,
            intent=intent,
            entities=entities,
            matched_event_id=matched_event_id,
            matched_event_title=matched_event_title,
            topics=topics,
            category_filter=None,
            date_start=date_start,
            date_end=date_end,
            date_label=date_label,
            wants_related=wants_related,
            wants_multiple=wants_multiple,
            requested_count=requested_count,
        )


query_analyzer = QueryAnalyzer()
