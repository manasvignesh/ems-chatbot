import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.connectors.ems import ems_connector
from app.rag.indexer import knowledge_indexer


@pytest.fixture(autouse=True)
async def seed_events():
    events = await ems_connector.fetch_public_events()
    for e in events:
        await knowledge_indexer.index_event(e, bot_id="ems")


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_bot_config_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/config/ems")
        assert response.status_code == 200
        data = response.json()
        assert data["bot_id"] == "ems"
        assert len(data["suggested_prompts"]) > 0


@pytest.mark.asyncio
async def test_chat_valid_event_query():
    payload = {
        "bot_id": "ems",
        "message": "What is HackVerse and when is it happening?",
        "conversation_id": "test-conv-101",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "answer" in data
        assert len(data["answer"]) > 0
        assert data["conversation_id"] == "test-conv-101"


@pytest.mark.asyncio
async def test_chat_out_of_scope_query():
    payload = {
        "bot_id": "ems",
        "message": "Who won yesterday's IPL cricket match?",
        "conversation_id": "test-conv-102",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "out_of_scope"
        assert data["cooldown_seconds"] == 10
        assert data["conversation_id"] == "test-conv-102"


@pytest.mark.asyncio
async def test_chat_page_context_flow():
    payload = {
        "bot_id": "ems",
        "message": "What is the team size and eligibility?",
        "conversation_id": "test-conv-103",
        "page_context": {
            "page_type": "event",
            "event_id": "hackverse-2026",
            "event_name": "HackVerse 2026",
        },
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
