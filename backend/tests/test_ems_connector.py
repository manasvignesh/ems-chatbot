import pytest
from app.connectors.ems import ems_connector


@pytest.mark.asyncio
async def test_fetch_equinox_events():
    events = await ems_connector.fetch_public_events()
    assert len(events) >= 10

    event_ids = [e.external_id for e in events]
    assert "equinox-2.0" in event_ids
    assert "spotlight" in event_ids
    assert "crossroads" in event_ids
    assert "startup-expo" in event_ids
    assert "brand-battles" in event_ids
    assert "ipl-auction" in event_ids
    assert "hustle-mania" in event_ids
    assert "internship-drive" in event_ids
    assert "startup-poly" in event_ids
    assert "e-cell-meet" in event_ids
    assert "pitch-deck" in event_ids


@pytest.mark.asyncio
async def test_fetch_single_equinox_subevent():
    event = await ems_connector.fetch_public_event("startup-poly")
    assert event is not None
    assert event.title == "Startup Poly"
    assert "Monopoly" in event.description
