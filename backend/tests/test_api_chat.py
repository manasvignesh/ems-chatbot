import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.scripts.reset_equinox_knowledge import reset_knowledge


@pytest.fixture(autouse=True)
async def setup_knowledge():
    await reset_knowledge(bot_id="ems")


@pytest.mark.asyncio
async def test_chat_valid_equinox_query():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/chat",
            json={"bot_id": "ems", "message": "What is Equinox 2.0?"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "Equinox" in data["answer"]


@pytest.mark.asyncio
async def test_chat_ipl_auction_query():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/chat",
            json={"bot_id": "ems", "message": "Tell me about IPL Auction in Equinox"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "IPL Auction" in data["answer"] or "cricket" in data["answer"].lower()


@pytest.mark.asyncio
async def test_chat_out_of_scope_rejection():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/chat",
            json={"bot_id": "ems", "message": "Who won yesterday's IPL match?"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "out_of_scope"
        assert data["cooldown_seconds"] in (2, 3)
        assert "ticket_number" in data
