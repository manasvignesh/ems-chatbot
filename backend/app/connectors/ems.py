from typing import Any, Dict, List, Optional
import httpx
from app.connectors.base import BaseEventConnector
from app.core.config import settings
from app.core.logging import logger
from app.models.event import EventKnowledge

# Authoritative Equinox 2.0 and sub-events dataset
DEFAULT_EMS_EVENTS: List[Dict[str, Any]] = [
    {
        "external_id": "equinox-2.0",
        "title": "The Equinox 2.0",
        "description": "Equinox is a premier two-day E-Summit at MLR Institute of Technology, Hyderabad (Tagline: 'Where Passion Meets Perseverance'). It brings students together to take on real-world business challenges, explore entrepreneurship, compete, connect with startups and investors, and gain practical experience.",
        "category": "E-Summit",
        "date": "30–31 October",
        "venue": "MLR Institute of Technology, Dundigal Police Station Road, Hyderabad – 500 043, Telangana",
        "organizer": "Centre for Innovation & Entrepreneurship (CIE), MLRIT",
        "club": "MLRIT CIE",
        "source_url": "/events/equinox-2.0",
        "status": "published",
        "rules": [
            "Open to all students interested in entrepreneurship, business, and innovation.",
            "Features 10 flagship sub-events including Spotlight, Crossroads, Startup Expo, Brand Battles, IPL Auction, Hustle Mania, Internship Drive, Startup Poly, E-Cell Meet, and Pitch Deck."
        ],
        "requirements": [
            "Check event desk at MLRIT campus during summit days."
        ],
        "schedule": "30–31 October across MLRIT Campus."
    },
    {
        "external_id": "spotlight",
        "title": "Spotlight",
        "description": "Features presentations from industry experts on technology, entrepreneurship, and startups. Students gain firsthand insights into emerging technologies, industry trends, and the future of entrepreneurship.",
        "category": "Keynote / Expert Talks",
        "date": "30–31 October",
        "venue": "MLR Institute of Technology, Hyderabad",
        "organizer": "MLRIT CIE",
        "source_url": "/events/spotlight",
        "status": "published"
    },
    {
        "external_id": "crossroads",
        "title": "Crossroads",
        "description": "A business case-study competition where teams analyse real-world business challenges and develop practical, actionable strategies. Develops problem-solving, decision-making, and critical business skills.",
        "category": "Competition",
        "date": "30–31 October",
        "venue": "MLR Institute of Technology, Hyderabad",
        "organizer": "MLRIT CIE",
        "source_url": "/events/crossroads",
        "status": "published"
    },
    {
        "external_id": "startup-expo",
        "title": "Startup Expo",
        "description": "Provides startups with a dedicated platform to showcase their products, business ideas, and solutions. Gives startups visibility and student exposure while enabling students to discover new businesses.",
        "category": "Exhibition / Expo",
        "date": "30–31 October",
        "venue": "MLR Institute of Technology, Hyderabad",
        "organizer": "MLRIT CIE",
        "source_url": "/events/startup-expo",
        "status": "published"
    },
    {
        "external_id": "brand-battles",
        "title": "Brand Battles",
        "description": "A competitive debate between teams representing rival brands from the same industry sector. Participants defend assigned brands using real-time examples, market data, and case studies while challenging opposing strategies.",
        "category": "Debate / Competition",
        "date": "30–31 October",
        "venue": "MLR Institute of Technology, Hyderabad",
        "organizer": "MLRIT CIE",
        "source_url": "/events/brand-battles",
        "status": "published"
    },
    {
        "external_id": "ipl-auction",
        "title": "IPL Auction",
        "description": "An interactive simulated cricket auction where participants act as team owners, manage virtual budgets, bid strategically for players, build balanced teams, and make high-stakes tactical decisions.",
        "category": "Simulation / Competition",
        "date": "30–31 October",
        "venue": "MLR Institute of Technology, Hyderabad",
        "organizer": "MLRIT CIE",
        "source_url": "/events/ipl-auction",
        "status": "published"
    },
    {
        "external_id": "hustle-mania",
        "title": "Hustle Mania",
        "description": "A live marketing and negotiation competition where students sell products of their choice and compete with peers. Develops persuasion, communication, salesmanship, and business negotiation skills.",
        "category": "Competition",
        "date": "30–31 October",
        "venue": "MLR Institute of Technology, Hyderabad",
        "organizer": "MLRIT CIE",
        "source_url": "/events/hustle-mania",
        "status": "published"
    },
    {
        "external_id": "internship-drive",
        "title": "Internship Drive",
        "description": "Connects students with visiting startups and companies offering internship opportunities. Enables students to explore career paths, gain practical experience, and build valuable professional networks.",
        "category": "Career / Hiring",
        "date": "30–31 October",
        "venue": "MLR Institute of Technology, Hyderabad",
        "organizer": "MLRIT CIE",
        "source_url": "/events/internship-drive",
        "status": "published"
    },
    {
        "external_id": "startup-poly",
        "title": "Startup Poly",
        "description": "A fast-paced business simulation game inspired by Monopoly where participants build startups, compete in dynamic markets, manage company finances, navigate risks, and make strategic decisions.",
        "category": "Simulation / Game",
        "date": "30–31 October",
        "venue": "MLR Institute of Technology, Hyderabad",
        "organizer": "MLRIT CIE",
        "source_url": "/events/startup-poly",
        "status": "published"
    },
    {
        "external_id": "e-cell-meet",
        "title": "E-Cell Meet",
        "description": "Brings together entrepreneurship cells (E-Cells) and student leaders from various colleges to share ideas, exchange experiences, build relationships, collaborate, and explore cross-campus partnerships.",
        "category": "Networking",
        "date": "30–31 October",
        "venue": "MLR Institute of Technology, Hyderabad",
        "organizer": "MLRIT CIE",
        "source_url": "/events/e-cell-meet",
        "status": "published"
    },
    {
        "external_id": "pitch-deck",
        "title": "Pitch Deck",
        "description": "A startup pitching platform where aspiring student founders present their business ideas directly to investors, startup mentors, and industry experts for feedback, insights, and guidance.",
        "category": "Pitching",
        "date": "30–31 October",
        "venue": "MLR Institute of Technology, Hyderabad",
        "organizer": "MLRIT CIE",
        "source_url": "/events/pitch-deck",
        "status": "published"
    }
]


class EMSEventConnector(BaseEventConnector):
    """Connector to ingest public events for The Equinox 2.0."""

    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url or settings.EMS_PUBLIC_API_URL

    def normalize_event_dict(self, raw: Dict[str, Any]) -> EventKnowledge:
        """Normalize raw EMS event dictionary to EventKnowledge model."""
        rules = raw.get("rules", [])
        if isinstance(rules, str):
            rules = [r.strip() for r in rules.split("\n") if r.strip()]

        reqs = raw.get("requirements", [])
        if isinstance(reqs, str):
            reqs = [r.strip() for r in reqs.split("\n") if r.strip()]

        return EventKnowledge(
            external_id=str(raw.get("external_id") or raw.get("id") or raw.get("slug") or raw.get("title", "event")).lower().replace(" ", "-"),
            title=raw.get("title", "The Equinox 2.0"),
            description=raw.get("description"),
            category=raw.get("category", "E-Summit"),
            date=raw.get("date", "30–31 October"),
            start_time=raw.get("start_time"),
            end_time=raw.get("end_time"),
            venue=raw.get("venue", "MLR Institute of Technology, Hyderabad"),
            organizer=raw.get("organizer", "MLRIT CIE"),
            club=raw.get("club", "MLRIT CIE"),
            registration_deadline=raw.get("registration_deadline"),
            eligibility=raw.get("eligibility"),
            team_size=raw.get("team_size"),
            prizes=raw.get("prizes"),
            rules=rules,
            requirements=reqs,
            schedule=raw.get("schedule"),
            source_url=raw.get("source_url") or f"/events/{raw.get('external_id')}",
            status=raw.get("status", "published"),
        )

    async def fetch_public_events(self) -> List[EventKnowledge]:
        """Fetch Equinox 2.0 events."""
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                response = await client.get(self.api_url)
                if response.status_code == 200:
                    data = response.json()
                    raw_events = data if isinstance(data, list) else data.get("events", [])
                    if raw_events:
                        logger.info(f"Fetched {len(raw_events)} events from live EMS API.")
                        return [self.normalize_event_dict(e) for e in raw_events]
        except Exception as e:
            logger.debug(f"Using Equinox 2.0 master catalog ({e}).")

        return [self.normalize_event_dict(e) for e in DEFAULT_EMS_EVENTS]

    async def fetch_public_event(self, event_id: str) -> Optional[EventKnowledge]:
        """Fetch single sub-event by ID or slug."""
        all_events = await self.fetch_public_events()
        for e in all_events:
            if e.external_id == event_id or e.external_id == event_id.lower():
                return e
        return None


ems_connector = EMSEventConnector()
