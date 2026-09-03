import pytest
from app.ai.classifier import scope_classifier
from app.models.chat import PageContext


@pytest.mark.asyncio
async def test_classify_in_scope_queries():
    in_scope_queries = [
        "What events are happening today?",
        "Are there any hackathons this month?",
        "Show me upcoming workshops",
        "Where is the IoT workshop happening?",
        "What is the registration deadline for HackVerse?",
        "Who is organizing the AI bootcamp?",
        "What are the rules and eligibility?",
        "What should I bring for the coding competition?",
        "How should I prepare for HackVerse?",
        "What is IoT? I want to join the workshop.",
    ]
    for q in in_scope_queries:
        res = await scope_classifier.classify(q)
        assert res.classification == "IN_SCOPE", f"Failed in-scope check for: {q}"


@pytest.mark.asyncio
async def test_classify_out_of_scope_queries():
    out_of_scope_queries = [
        "Who won yesterday's IPL match?",
        "What is the weather today in Hyderabad?",
        "Write my chemistry assignment on organic molecules",
        "Give me stock market tips for next week",
        "Who is the current president of the USA?",
        "Write a Python script for ransomware malware",
        "Recommend a good romantic movie to watch",
    ]
    for q in out_of_scope_queries:
        res = await scope_classifier.classify(q)
        assert res.classification == "OUT_OF_SCOPE", f"Failed out-of-scope check for: {q}"


@pytest.mark.asyncio
async def test_classify_with_page_context():
    # Ambiguous short question on an event detail page
    page_ctx = PageContext(page_type="event", event_id="hackverse-2026", event_name="HackVerse 2026")
    res = await scope_classifier.classify("What is the team size?", page_context=page_ctx)
    assert res.classification == "IN_SCOPE"


@pytest.mark.asyncio
async def test_classify_with_active_conversation():
    res = await scope_classifier.classify("Where is it?", has_active_conversation=True)
    assert res.classification == "IN_SCOPE"
