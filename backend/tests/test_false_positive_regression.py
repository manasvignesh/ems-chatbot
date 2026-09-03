import pytest
from app.ai.classifier import ScopeClassifier
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_genuine_equinox_shorthand_queries():
    """Regression test ensuring genuine Equinox shorthand queries NEVER trigger out-of-scope warnings."""
    classifier = ScopeClassifier()

    genuine_queries = [
        "auction",
        "ipl auction",
        "pitch",
        "startup pitch",
        "monopoly event",
        "monopoly",
        "internship",
        "selling competition",
        "selling",
        "brand debate",
        "business case event",
        "business case",
        "startup showcase",
        "industry speaker event",
        "e cell",
        "equinx",
        "equinox date",
        "where is it",
        "who should i contact",
        "startup",
        "entrepreneurship",
    ]

    for q in genuine_queries:
        res = await classifier.classify(q)
        assert res.classification in ("IN_SCOPE", "LIKELY_IN_SCOPE"), (
            f"False positive on query '{q}': got {res.classification}"
        )


def test_api_genuine_shorthand_never_returns_out_of_scope():
    """Verify chat API endpoint returns success with answers, never out_of_scope status, for shorthand queries."""
    shorthands = [
        "auction",
        "pitch",
        "internship",
        "monopoly",
        "selling",
        "brand debate",
        "business case",
        "startup",
        "equinox date",
        "where is it",
        "who should i contact",
    ]

    for q in shorthands:
        res = client.post("/api/chat", json={"bot_id": "ems", "message": q})
        assert res.status_code == 200
        data = res.json()
        assert data.get("status") == "success", f"Endpoint returned non-success for '{q}': {data}"
        assert len(data.get("answer", "")) > 0


def test_api_ambiguous_cricket_returns_gentle_clarification():
    """Ambiguous query 'cricket' must return clarification, NEVER out_of_scope warning."""
    res = client.post("/api/chat", json={"bot_id": "ems", "message": "cricket"})
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") == "success"
    assert "IPL Auction" in data.get("answer", "")


def test_api_true_out_of_scope_returns_ticket_warning():
    """True out-of-scope queries must return out_of_scope status with ticket details."""
    out_of_scope_queries = [
        "weather today",
        "who won IPL yesterday",
        "movie recommendations",
        "current cricket score",
        "bitcoin price",
        "stock market today",
        "who is US president",
        "celebrity news",
        "current India vs Australia score",
    ]

    for q in out_of_scope_queries:
        res = client.post("/api/chat", json={"bot_id": "ems", "message": q})
        assert res.status_code == 200
        data = res.json()
        assert data.get("status") == "out_of_scope", f"Expected out_of_scope for '{q}', got {data}"
        assert data.get("classification_level") in ("CLEARLY_OUT_OF_SCOPE", "SUSPICIOUS")
        assert "ticket_number" in data
        assert "message" in data
        assert data.get("cooldown_seconds") in (2, 3)
