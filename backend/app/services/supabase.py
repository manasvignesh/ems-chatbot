import uuid
import numpy as np
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logging import logger
from app.models.knowledge import KnowledgeChunk, KnowledgeSourceCreate

try:
    from supabase import create_client, Client
    SUPABASE_LIB_AVAILABLE = True
except ImportError:
    SUPABASE_LIB_AVAILABLE = False


class InMemoryVectorStore:
    """Fast in-memory store for chunks and sources when Supabase is not configured or in offline mode."""

    def __init__(self):
        self.sources: Dict[str, Dict[str, Any]] = {}
        self.chunks: List[Dict[str, Any]] = []

    def clear(self):
        self.sources.clear()
        self.chunks.clear()

    def add_source(self, source_dict: Dict[str, Any]) -> str:
        s_id = str(source_dict.get("id") or uuid.uuid4())
        source_dict["id"] = s_id
        source_dict["created_at"] = datetime.now(timezone.utc).isoformat()
        self.sources[s_id] = source_dict
        return s_id

    def delete_source_by_external_id(self, external_id: str, bot_id: str = "ems"):
        s_ids_to_del = [
            s_id for s_id, s in self.sources.items()
            if s.get("external_id") == external_id and s.get("bot_id") == bot_id
        ]
        for s_id in s_ids_to_del:
            self.delete_source(s_id)

    def delete_source(self, source_id: str):
        if source_id in self.sources:
            del self.sources[source_id]
        self.chunks = [c for c in self.chunks if str(c.get("source_id")) != str(source_id)]

    def add_chunks(self, chunks: List[KnowledgeChunk], source_id: str):
        for c in chunks:
            c_dict = c.model_dump()
            c_dict["id"] = str(uuid.uuid4())
            c_dict["source_id"] = source_id
            c_dict["created_at"] = datetime.now(timezone.utc).isoformat()
            self.chunks.append(c_dict)

    def match_chunks(
        self,
        query_embedding: List[float],
        bot_id: str = "ems",
        event_id: Optional[str] = None,
        top_k: int = 6,
        threshold: float = 0.35,
    ) -> List[Dict[str, Any]]:
        if not self.chunks or not query_embedding:
            return []

        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []
        q_unit = q_vec / q_norm

        results = []
        for c in self.chunks:
            if c.get("bot_id") != bot_id:
                continue

            metadata = c.get("metadata", {})
            if event_id and metadata.get("event_id") != event_id:
                continue

            c_emb = c.get("embedding")
            if not c_emb:
                continue

            c_vec = np.array(c_emb, dtype=np.float32)
            c_norm = np.linalg.norm(c_vec)
            if c_norm == 0:
                continue
            c_unit = c_vec / c_norm

            sim = float(np.dot(q_unit, c_unit))
            if sim >= threshold:
                results.append({
                    "id": c.get("id"),
                    "source_id": c.get("source_id"),
                    "content": c.get("content"),
                    "metadata": metadata,
                    "similarity": sim,
                })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def get_all_chunks(self, bot_id: str = "ems") -> List[Dict[str, Any]]:
        return [c for c in self.chunks if c.get("bot_id") == bot_id]


class SupabaseService:
    """Database service managing Supabase pgvector and in-memory fallback."""

    def __init__(self):
        self.client: Optional[Client] = None
        self.in_memory = InMemoryVectorStore()
        self.is_connected = False

        if (
            SUPABASE_LIB_AVAILABLE
            and settings.SUPABASE_URL
            and (settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY)
        ):
            try:
                key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
                self.client = create_client(settings.SUPABASE_URL, key)
                self.is_connected = True
                logger.info("Connected to Supabase PostgreSQL.")
            except Exception as e:
                logger.warning(f"Failed to connect to Supabase: {e}. Falling back to in-memory store.")
                self.is_connected = False
        else:
            logger.info("Running in memory-backed mode (Supabase URL/key not supplied).")

    async def save_source_and_chunks(
        self,
        bot_id: str,
        source_type: str,
        title: str,
        content_hash: str,
        chunks: List[KnowledgeChunk],
        external_id: Optional[str] = None,
        source_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Save a knowledge source and its embedded chunks."""
        metadata = metadata or {}
        source_id = str(uuid.uuid4())

        # If live Supabase is active
        if self.is_connected and self.client:
            try:
                # 1. Upsert source
                source_data = {
                    "id": source_id,
                    "bot_id": bot_id,
                    "source_type": source_type,
                    "external_id": external_id,
                    "title": title,
                    "source_url": source_url,
                    "content_hash": content_hash,
                    "status": "ready",
                    "metadata": metadata,
                }
                self.client.table("knowledge_sources").upsert(source_data).execute()

                # 2. Insert chunks
                chunk_rows = []
                for c in chunks:
                    chunk_rows.append({
                        "bot_id": bot_id,
                        "source_id": source_id,
                        "chunk_index": c.chunk_index,
                        "content": c.content,
                        "embedding": c.embedding,
                        "metadata": c.metadata,
                    })
                if chunk_rows:
                    self.client.table("knowledge_chunks").insert(chunk_rows).execute()
                
                # Also cache in memory for ultra-fast hybrid search
                self.in_memory.add_source(source_data)
                self.in_memory.add_chunks(chunks, source_id)
                return source_id
            except Exception as e:
                logger.error(f"Supabase write error: {e}. Falling back to in-memory save.")

        # In-Memory fallback
        source_data = {
            "id": source_id,
            "bot_id": bot_id,
            "source_type": source_type,
            "external_id": external_id,
            "title": title,
            "source_url": source_url,
            "content_hash": content_hash,
            "status": "ready",
            "metadata": metadata,
        }
        self.in_memory.add_source(source_data)
        self.in_memory.add_chunks(chunks, source_id)
        return source_id

    async def search_chunks_vector(
        self,
        query_embedding: List[float],
        bot_id: str = "ems",
        event_id: Optional[str] = None,
        top_k: int = 6,
        threshold: float = 0.35,
    ) -> List[Dict[str, Any]]:
        """Vector similarity retrieval."""
        if self.is_connected and self.client:
            try:
                rpc_params = {
                    "query_embedding": query_embedding,
                    "match_threshold": threshold,
                    "match_count": top_k,
                    "filter_bot_id": bot_id,
                    "filter_event_id": event_id,
                }
                response = self.client.rpc("match_knowledge_chunks", rpc_params).execute()
                if response.data:
                    return response.data
            except Exception as e:
                logger.warning(f"Supabase RPC match_knowledge_chunks error: {e}. Using in-memory match.")

        return self.in_memory.match_chunks(
            query_embedding=query_embedding,
            bot_id=bot_id,
            event_id=event_id,
            top_k=top_k,
            threshold=threshold,
        )

    def get_source_by_external_id(self, external_id: str, bot_id: str = "ems") -> Optional[Dict[str, Any]]:
        """Get source by external EMS event ID."""
        for s in self.in_memory.sources.values():
            if s.get("external_id") == external_id and s.get("bot_id") == bot_id:
                return s
        return None

    def delete_by_external_id(self, external_id: str, bot_id: str = "ems"):
        """Delete knowledge source and chunks by external event ID."""
        if self.is_connected and self.client:
            try:
                self.client.table("knowledge_sources").delete().eq("external_id", external_id).eq("bot_id", bot_id).execute()
            except Exception as e:
                logger.error(f"Supabase delete error: {e}")
        self.in_memory.delete_source_by_external_id(external_id, bot_id)


supabase_service = SupabaseService()
