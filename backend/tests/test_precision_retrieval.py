import pytest
from app.rag.hybrid_search import hybrid_search_engine
from app.scripts.reset_equinox_knowledge import reset_knowledge


@pytest.fixture(autouse=True)
async def setup_index():
    await reset_knowledge(bot_id="ems")


@pytest.mark.asyncio
async def test_startup_poly_monopoly_precision():
    """Test 'monopoly event' returns ONLY Startup Poly."""
    chunks, cards, sources = await hybrid_search_engine.search("monopoly event", bot_id="ems")
    assert len(cards) == 1
    assert cards[0].event_id == "startup-poly"
    assert "Startup Poly" in cards[0].title


@pytest.mark.asyncio
async def test_ipl_auction_cricket_precision():
    """Test 'cricket bidding' returns ONLY IPL Auction."""
    chunks, cards, sources = await hybrid_search_engine.search("cricket bidding", bot_id="ems")
    assert len(cards) == 1
    assert cards[0].event_id == "ipl-auction"
    assert "IPL Auction" in cards[0].title


@pytest.mark.asyncio
async def test_internship_drive_precision():
    """Test 'internship opportunities' returns ONLY Internship Drive."""
    chunks, cards, sources = await hybrid_search_engine.search("internship opportunities", bot_id="ems")
    assert len(cards) == 1
    assert cards[0].event_id == "internship-drive"


@pytest.mark.asyncio
async def test_pitch_deck_precision():
    """Test 'pitch startup idea' returns ONLY Pitch Deck."""
    chunks, cards, sources = await hybrid_search_engine.search("pitch startup idea", bot_id="ems")
    assert len(cards) == 1
    assert cards[0].event_id == "pitch-deck"
