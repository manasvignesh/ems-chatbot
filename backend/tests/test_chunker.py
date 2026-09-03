import pytest
from app.models.event import EventKnowledge
from app.rag.chunker import knowledge_chunker


def test_chunk_event():
    event = EventKnowledge(
        external_id="test-hackathon",
        title="Test National Hackathon",
        description="A great 24 hour event for developers to innovate.",
        category="Hackathon",
        date="2026-10-10",
        start_time="09:00 AM",
        end_time="09:00 AM (Next day)",
        venue="CIE Lab 1",
        organizer="CIE Club",
        registration_deadline="2026-10-05",
        eligibility="Undergrads",
        team_size="2 to 4 members",
        prizes="₹30,000 cash prizes",
        rules=["Bring your own laptop", "No pre-built code"],
        requirements=["College ID"],
        schedule="Day 1: Start at 9am. Day 2: Pitch at 9am.",
    )

    chunks = knowledge_chunker.chunk_event(event, bot_id="ems")
    assert len(chunks) >= 4

    sections = [c.metadata.get("section") for c in chunks]
    assert "overview" in sections
    assert "registration" in sections
    assert "schedule" in sections
    assert "rules" in sections

    for c in chunks:
        assert c.metadata.get("event_id") == "test-hackathon"
        assert c.bot_id == "ems"


def test_chunk_text():
    text = (
        "MLRIT Centre for Innovation and Entrepreneurship provides incubation and mentorship. "
        "Students can build startups and participate in hackathons across the year.\n\n"
        "Guidelines for event organizers:\n"
        "All events must be approved by the faculty coordinator prior to publishing."
    )
    chunks = knowledge_chunker.chunk_text(text, title="CIE Guidelines", source_type="markdown", bot_id="ems")
    assert len(chunks) >= 1
    assert "CIE Guidelines" in chunks[0].content
