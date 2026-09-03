import time
from typing import List
from app.connectors.ems import ems_connector
from app.core.logging import logger
from app.models.knowledge import SyncReport
from app.rag.indexer import knowledge_indexer


class KnowledgeService:
    """Coordinates indexing and synchronization pipelines."""

    async def sync_ems_events(self, bot_id: str = "ems") -> SyncReport:
        """Fetch all public EMS events and synchronize knowledge chunks."""
        start_time = time.time()
        events = await ems_connector.fetch_public_events()

        added = 0
        updated = 0
        unchanged = 0
        failed = 0

        for event in events:
            try:
                res = await knowledge_indexer.index_event(event, bot_id=bot_id)
                if res.status == "ready":
                    added += 1
                elif res.status == "unchanged":
                    unchanged += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Error syncing event {event.title}: {e}")
                failed += 1

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"EMS Sync complete: {len(events)} events processed (added/updated: {added}, unchanged: {unchanged}, failed: {failed}) in {duration_ms:.1f}ms."
        )

        return SyncReport(
            status="completed" if failed == 0 else "completed_with_errors",
            total_events=len(events),
            added_count=added,
            updated_count=updated,
            deleted_count=0,
            unchanged_count=unchanged,
            duration_ms=duration_ms,
            error_log=f"{failed} event(s) failed during indexing." if failed > 0 else None,
        )


knowledge_service = KnowledgeService()
