import pytest
from app.rag.hybrid_search import hybrid_search_engine
from app.scripts.reset_equinox_knowledge import reset_knowledge


@pytest.fixture(autouse=True)
async def setup_index():
    await reset_knowledge(bot_id="ems")


@pytest.mark.asyncio
async def test_hybrid_search_subevent_match():
    chunks, cards, sources = await hybrid_search_engine.search("What is Startup Poly?", bot_id="ems")
    assert len(chunks) > 0
    assert len(cards) >= 1
    assert cards[0].event_id == "startup-poly"
    assert "Startup Poly" in cards[0].title


@pytest.mark.asyncio
async def test_hybrid_search_sponsorship_query():
    chunks, cards, sources = await hybrid_search_engine.search("What are the sponsorship tiers?", bot_id="ems")
    assert len(chunks) > 0
    combined = " ".join([c.get("content", "") for c in chunks])
    assert "Associate" in combined or "Title Sponsor" in combined or "₹20,000" in combined
