from typing import List, Optional
from pydantic import BaseModel, Field


class EventKnowledge(BaseModel):
    """Normalized public event knowledge model for EMS."""
    external_id: str = Field(..., description="Unique event identifier from EMS (slug or UUID)")
    title: str = Field(..., description="Official title of the event")
    description: Optional[str] = Field(None, description="Detailed public description")
    category: Optional[str] = Field(None, description="Event category: Hackathon, Workshop, Seminar, etc.")
    date: Optional[str] = Field(None, description="Human-readable or ISO event date")
    start_time: Optional[str] = Field(None, description="Event start time")
    end_time: Optional[str] = Field(None, description="Event end time")
    venue: Optional[str] = Field(None, description="Campus venue, lab, auditorium, or virtual link")
    organizer: Optional[str] = Field(None, description="Organizing club, department, or committee")
    club: Optional[str] = Field(None, description="Club name if applicable")
    registration_deadline: Optional[str] = Field(None, description="Registration cutoff date and time")
    eligibility: Optional[str] = Field(None, description="Eligibility criteria (e.g., all years, CSE, etc.)")
    team_size: Optional[str] = Field(None, description="Team size specifications (e.g., 2-4 members, individual)")
    prizes: Optional[str] = Field(None, description="Prize pool, cash awards, certificates, or perks")
    rules: Optional[List[str]] = Field(default_factory=list, description="List of official rules and guidelines")
    requirements: Optional[List[str]] = Field(default_factory=list, description="What to bring or prerequisite skills")
    schedule: Optional[str] = Field(None, description="Detailed timeline or agenda")
    source_url: Optional[str] = Field(None, description="Direct URL to the event page on EMS")
    status: Optional[str] = Field("published", description="Event publication status (e.g. published, upcoming)")
