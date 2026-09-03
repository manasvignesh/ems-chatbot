from typing import Any, Dict, List, Optional
from app.rag.embeddings import embedding_service
from app.services.supabase import supabase_service
from app.core.config import settings
from app.core.logging import logger


class VectorRetriever:
    """Retrieves semantically relevant knowledge chunks via dense embeddings."""

    async def retrieve(
        self,
        query: str,
        bot_id: str = "ems",
        event_id: Optional[str] = None,
        top_k: int = 6,
        threshold: float = 0.30,
    ) -> List[Dict[str, Any]]:
        if not query.strip():
            return []

        try:
            # Generate query embedding
            query_emb = await embedding_service.get_embedding(query)

            # Query vector store
            chunks = await supabase_service.search_chunks_vector(
                query_embedding=query_emb,
                bot_id=bot_id,
                event_id=event_id,
                top_k=top_k,
                threshold=threshold,
            )
            return chunks
        except Exception as e:
            logger.error(f"Vector retrieval error: {e}")
            return []


vector_retriever = VectorRetriever()
