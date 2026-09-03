import pytest
from app.connectors.ems import ems_connector
from app.rag.hybrid_search import hybrid_search_engine
from app.rag.indexer import knowledge_indexer
from app.models.chat import PageContext


@pytest.mark.asyncio
async def test_hybrid_search_exact_match():
    # Index test events
    events = await ems_connector.fetch_public_events()
    for e in events:
        await knowledge_indexer.index_event(e, bot_id="ems")

    chunks, cards, sources = await hybrid_search_engine.search("Where is HackVerse?", bot_id="ems")
    assert len(chunks) > 0
    # HackVerse card should be present
    assert any("HackVerse" in card.title for card in cards)


@pytest.mark.asyncio
async def test_hybrid_search_page_context():
    page_ctx = PageContext(page_type="event", event_id="iot-robotics-workshop", event_name="IoT Workshop")
    chunks, cards, sources = await hybrid_search_engine.search(
        "What is the venue?",
        bot_id="ems",
        page_context=page_ctx
    )
    assert len(chunks) > 0
    assert any(c.get("metadata", {}).get("event_id") == "iot-robotics-workshop" for c in chunks)
