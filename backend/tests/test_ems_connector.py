import pytest
from app.connectors.ems import ems_connector, DEFAULT_EMS_EVENTS
from app.rag.indexer import knowledge_indexer


@pytest.mark.asyncio
async def test_fetch_public_events():
    events = await ems_connector.fetch_public_events()
    assert len(events) >= 4
    for e in events:
        assert e.title
        assert e.external_id
        assert e.category


@pytest.mark.asyncio
async def test_event_indexing_deduplication():
    event = ems_connector.normalize_event_dict(DEFAULT_EMS_EVENTS[0])
    res1 = await knowledge_indexer.index_event(event, bot_id="ems")
    assert res1.status in ("ready", "unchanged")

    # Second indexing without changes should be skipped
    res2 = await knowledge_indexer.index_event(event, bot_id="ems")
    assert res2.status == "unchanged"
    assert res2.chunks_created == 0
