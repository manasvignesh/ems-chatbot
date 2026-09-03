from fastapi import APIRouter, Query
from app.models.knowledge import SyncReport
from app.services.knowledge import knowledge_service

router = APIRouter(prefix="/sync", tags=["EMS Sync"])


@router.post("/ems", response_model=SyncReport)
async def sync_ems_public_events(bot_id: str = Query("ems")):
    """Trigger synchronization of public events from EMS into the vector RAG store."""
    return await knowledge_service.sync_ems_events(bot_id=bot_id)
