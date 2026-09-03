import pytest
from app.connectors.ems import ems_connector
from app.rag.hybrid_search import hybrid_search_engine
from app.rag.indexer import knowledge_indexer


@pytest.fixture(autouse=True)
async def setup_index():
    events = await ems_connector.fetch_public_events()
    for e in events:
        await knowledge_indexer.index_event(e, bot_id="ems")


@pytest.mark.asyncio
async def test_gen_ai_precision_isolation():
    """
    CRITICAL TEST:
    When user asks for 'gen ai' (or 'generative ai'), the chatbot must return ONLY the
    Autonomous AI Agents & GenAI Bootcamp and MUST NOT return HackVerse 2026 or IoT Workshop!
    """
    chunks, cards, sources = await hybrid_search_engine.search("gen ai", bot_id="ems")

    assert len(cards) == 1, f"Expected 1 card for 'gen ai', got {len(cards)}: {[c.title for c in cards]}"
    assert cards[0].event_id == "ai-agents-bootcamp"
    assert "Autonomous AI Agents" in cards[0].title or "GenAI" in cards[0].title

    # Explicitly ensure HackVerse is NOT present
    card_ids = [c.event_id for c in cards]
    assert "hackverse-2026" not in card_ids
    assert "iot-robotics-workshop" not in card_ids


@pytest.mark.asyncio
async def test_gen_ai_typo_precision_isolation():
    """Test 'genrative ai' typo returns only GenAI Bootcamp."""
    chunks, cards, sources = await hybrid_search_engine.search("genrative ai", bot_id="ems")
    assert len(cards) == 1
    assert cards[0].event_id == "ai-agents-bootcamp"
    assert "hackverse-2026" not in [c.event_id for c in cards]


@pytest.mark.asyncio
async def test_hackverse_precision_isolation():
    """Test 'hackverse' returns only HackVerse."""
    chunks, cards, sources = await hybrid_search_engine.search("hackverse", bot_id="ems")
    assert len(cards) == 1
    assert cards[0].event_id == "hackverse-2026"


@pytest.mark.asyncio
async def test_iot_precision_isolation():
    """Test 'iot worshop' typo returns only IoT Workshop."""
    chunks, cards, sources = await hybrid_search_engine.search("iot worshop", bot_id="ems")
    assert len(cards) == 1
    assert cards[0].event_id == "iot-robotics-workshop"
