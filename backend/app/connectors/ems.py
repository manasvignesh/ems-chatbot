from typing import Any, Dict, List, Optional
import httpx
from app.connectors.base import BaseEventConnector
from app.core.config import settings
from app.core.logging import logger
from app.models.event import EventKnowledge

# Rich baseline public event dataset for MLRIT CIE EMS
DEFAULT_EMS_EVENTS: List[Dict[str, Any]] = [
    {
        "external_id": "hackverse-2026",
        "title": "HackVerse 2026",
        "description": "MLRIT's premier 24-hour national hackathon focused on building innovative solutions in Artificial Intelligence, Smart Healthcare, and Sustainable Technologies. Hosted by the Centre for Innovation & Entrepreneurship (CIE).",
        "category": "Hackathon",
        "date": "2026-09-12 to 2026-09-13",
        "start_time": "09:00 AM (Day 1)",
        "end_time": "05:00 PM (Day 2)",
        "venue": "Centre for Innovation & Entrepreneurship (CIE Block), 3rd Floor Labs, MLRIT Campus",
        "organizer": "CIE Innovation Club & Department of CSE",
        "club": "CIE Innovators",
        "registration_deadline": "2026-09-08 11:59 PM",
        "eligibility": "Open to all undergraduate and postgraduate engineering students from any year or branch.",
        "team_size": "2 to 4 members per team",
        "prizes": "₹50,000 Total Prize Pool (1st Prize: ₹25,000, 2nd Prize: ₹15,000, 3rd Prize: ₹10,000) plus direct incubation mentorship from CIE.",
        "rules": [
            "All code, designs, and prototypes must be developed fresh during the 24-hour hackathon period.",
            "Open source libraries, APIs, and frameworks are permitted with proper attribution.",
            "Every team must submit their code repository on GitHub and provide a 3-minute working demo during the evaluation round.",
            "Plagiarism or submission of pre-existing commercial projects will lead to immediate disqualification."
        ],
        "requirements": [
            "College ID card is strictly mandatory for physical entry.",
            "Bring your own laptops, chargers, extension cords, and hardware development kits if working on IoT tracks.",
            "Ensure necessary IDEs and software packages are pre-installed before reporting to the venue."
        ],
        "schedule": "Day 1: 09:00 AM Registration & Check-in | 10:00 AM Opening Ceremony | 11:00 AM Hacking Commences | 03:00 PM Mentoring Round 1 | 08:00 PM Dinner | Day 2: 08:00 AM Breakfast | 11:00 AM Hacking Concludes | 01:00 PM Project Pitches | 04:30 PM Award Ceremony.",
        "source_url": "/events/hackverse-2026",
        "status": "published"
    },
    {
        "external_id": "iot-robotics-workshop",
        "title": "Hands-on IoT & Embedded Systems Workshop",
        "description": "A comprehensive practical workshop on microcontroller programming (ESP32/Raspberry Pi), sensor interfacing, and cloud MQTT telemetry integration. Ideal for beginners and hardware enthusiasts.",
        "category": "Workshop",
        "date": "2026-09-05",
        "start_time": "10:00 AM",
        "end_time": "04:30 PM",
        "venue": "Embedded Systems Lab (Room 214), ECE Block, MLRIT",
        "organizer": "Robotics & IoT Club (RIoT) in collaboration with CIE",
        "club": "RIoT Club",
        "registration_deadline": "2026-09-04 06:00 PM",
        "eligibility": "Open to all 1st, 2nd, and 3rd year engineering students (ECE, EEE, CSE, IT, MECH, AERO).",
        "team_size": "Individual registration (Hardware kits will be provided in pairs during the lab).",
        "prizes": "Certificate of Completion recognized by MLRIT CIE + Free take-home sensor starter kit for top 5 performers.",
        "rules": [
            "Attendance for the full duration is mandatory to receive the certification.",
            "Laboratory equipment and development boards must be handled with care.",
            "Participants should install Arduino IDE and VS Code before the session."
        ],
        "requirements": [
            "Personal laptop with Wi-Fi capability and USB ports.",
            "Arduino IDE v2.x installed.",
            "Micro-USB or Type-C data cable."
        ],
        "schedule": "10:00 AM Introduction to ESP32 Architecture | 11:30 AM Hands-on GPIO & Sensor Interfacing | 01:00 PM Lunch Break | 02:00 PM Cloud Telemetry & MQTT Dashboard Setup | 04:00 PM Q&A and Certificate Distribution.",
        "source_url": "/events/iot-robotics-workshop",
        "status": "published"
    },
    {
        "external_id": "ai-agents-bootcamp",
        "title": "Autonomous AI Agents & GenAI Bootcamp",
        "description": "Deep dive into building multi-agent systems, Retrieval-Augmented Generation (RAG), and reasoning agents using modern LLM frameworks and vector databases.",
        "category": "Seminar",
        "date": "2026-09-09",
        "start_time": "02:00 PM",
        "end_time": "05:00 PM",
        "venue": "Main Auditorium, MLRIT Central Block",
        "organizer": "AI & Data Science Student Chapter",
        "club": "AI Mavericks",
        "registration_deadline": "2026-09-08 05:00 PM",
        "eligibility": "All students interested in Artificial Intelligence and Software Engineering.",
        "team_size": "Individual",
        "prizes": "E-Certificates for all attendees + $50 Cloud LLM API credits for workshop participants.",
        "rules": [
            "Seats are allotted on a first-come, first-served basis.",
            "Maintain auditorium decorum during keynote speaker presentations."
        ],
        "requirements": [
            "Notebook and laptop (optional for live code-along session)."
        ],
        "schedule": "02:00 PM Welcome Address | 02:15 PM Keynote on Agentic AI & RAG Architectures | 03:45 PM Interactive Live Agent Coding | 04:45 PM Q&A with Industry Speakers.",
        "source_url": "/events/ai-agents-bootcamp",
        "status": "published"
    },
    {
        "external_id": "cybershield-ctf",
        "title": "CyberShield Capture The Flag (CTF)",
        "description": "An intense jeopardy-style cybersecurity competition featuring challenges in web exploitation, cryptography, reverse engineering, and digital forensics.",
        "category": "Competition",
        "date": "2026-09-18",
        "start_time": "01:00 PM",
        "end_time": "07:00 PM",
        "venue": "Cyber Security Research Lab (Lab 4), MLRIT",
        "organizer": "Null Byte Security Club",
        "club": "Null Byte",
        "registration_deadline": "2026-09-16 10:00 PM",
        "eligibility": "Open to all college students. Basic knowledge of networking and Linux command line recommended.",
        "team_size": "Teams of 1 to 3 members",
        "prizes": "1st Prize: ₹15,000 + Security Course Vouchers | 2nd Prize: ₹8,000 | 3rd Prize: ₹4,000.",
        "rules": [
            "Attacking the competition infrastructure or fellow contestants' machines is strictly prohibited and results in permanent ban.",
            "Flag sharing between different teams will lead to instant disqualification.",
            "Use of automated DDoS tools against the scoreboard server is forbidden."
        ],
        "requirements": [
            "Laptop running Kali Linux, Ubuntu, or WSL with security utilities.",
            "Discord account for live challenge hints and announcements."
        ],
        "schedule": "01:00 PM Platform Access & Rules Briefing | 01:30 PM CTF Challenge Begins | 06:30 PM CTF Closes & Write-up Verification | 07:00 PM Winner Announcement.",
        "source_url": "/events/cybershield-ctf",
        "status": "published"
    }
]


class EMSEventConnector(BaseEventConnector):
    """Connector to ingest public events from the MLRIT CIE EMS platform."""

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
            title=raw.get("title", "Untitled Event"),
            description=raw.get("description"),
            category=raw.get("category", "General"),
            date=raw.get("date"),
            start_time=raw.get("start_time"),
            end_time=raw.get("end_time"),
            venue=raw.get("venue"),
            organizer=raw.get("organizer"),
            club=raw.get("club"),
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
        """Fetch public events from live EMS API or fallback to rich default dataset."""
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.get(self.api_url)
                if response.status_code == 200:
                    data = response.json()
                    raw_events = data if isinstance(data, list) else data.get("events", [])
                    if raw_events:
                        logger.info(f"Fetched {len(raw_events)} events from live EMS API.")
                        return [self.normalize_event_dict(e) for e in raw_events]
        except Exception as e:
            logger.info(f"EMS Live API not reachable ({e}). Using default seed event catalog.")

        # Fallback to rich default dataset
        return [self.normalize_event_dict(e) for e in DEFAULT_EMS_EVENTS]

    async def fetch_public_event(self, event_id: str) -> Optional[EventKnowledge]:
        """Fetch single event by ID or slug."""
        all_events = await self.fetch_public_events()
        for e in all_events:
            if e.external_id == event_id or e.external_id == event_id.lower():
                return e
        return None


ems_connector = EMSEventConnector()
