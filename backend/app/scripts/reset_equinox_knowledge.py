import asyncio
import os
from app.connectors.ems import ems_connector
from app.core.logging import logger
from app.rag.chunker import knowledge_chunker
from app.rag.embeddings import embedding_service
from app.rag.indexer import knowledge_indexer
from app.services.supabase import supabase_service


async def reset_knowledge(bot_id: str = "ems"):
    """Reset and rebuild vector RAG storage with strictly Equinox 2.0 knowledge."""
    logger.info("Starting complete reset of RAG knowledge for Equinox 2.0...")

    # 1. Clear in-memory / cache storage
    supabase_service.in_memory.clear()

    # 2. If live Supabase is active, clear old tables
    if supabase_service.is_connected and supabase_service.client:
        try:
            supabase_service.client.table("knowledge_chunks").delete().eq("bot_id", bot_id).execute()
            supabase_service.client.table("knowledge_sources").delete().eq("bot_id", bot_id).execute()
            logger.info("Purged existing Supabase knowledge_chunks and knowledge_sources.")
        except Exception as e:
            logger.warning(f"Error purging Supabase tables: {e}")

    # 3. Index all Equinox 2.0 sub-events
    events = await ems_connector.fetch_public_events()
    indexed_events_count = 0
    for event in events:
        res = await knowledge_indexer.index_event(event, bot_id=bot_id)
        if res.status in ("ready", "unchanged"):
            indexed_events_count += 1
    logger.info(f"Indexed {indexed_events_count} Equinox events and sub-events.")

    # 4. Index the Master Equinox Markdown Document
    md_path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "equinox_master_knowledge.md")
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        chunks = knowledge_chunker.chunk_text(
            text=md_content,
            title="The Equinox 2.0 Master Knowledge Document",
            source_type="markdown",
            bot_id=bot_id,
            extra_metadata={"event": "The Equinox 2.0", "source": "brochure_and_prospectus"}
        )

        chunk_texts = [c.content for c in chunks]
        embeddings = await embedding_service.get_batch_embeddings(chunk_texts)
        for i, emb in enumerate(embeddings):
            chunks[i].embedding = emb

        content_hash = knowledge_indexer.calculate_hash(md_content)
        await supabase_service.save_source_and_chunks(
            bot_id=bot_id,
            source_type="markdown",
            title="The Equinox 2.0 Master Knowledge Document",
            content_hash=content_hash,
            chunks=chunks,
            metadata={"event": "The Equinox 2.0"}
        )
        logger.info(f"Indexed Master Knowledge Document with {len(chunks)} chunks.")

    total_chunks = len(supabase_service.in_memory.chunks)
    logger.info(f"Equinox knowledge reset COMPLETE. Total active knowledge chunks: {total_chunks}")
    return total_chunks


if __name__ == "__main__":
    asyncio.run(reset_knowledge())
