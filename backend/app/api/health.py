from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings
from app.services.supabase import supabase_service

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check endpoint providing system status."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "supabase_connected": supabase_service.is_connected,
        "gemini_model": settings.GEMINI_MODEL,
        "embedding_model": settings.GOOGLE_EMBEDDING_MODEL,
    }
