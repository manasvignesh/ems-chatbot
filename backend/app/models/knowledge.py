from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field


class KnowledgeSourceCreate(BaseModel):
    """Payload for creating a text or markdown knowledge source."""
    bot_id: str = "ems"
    title: str
    content: str
    source_type: str = "text"  # 'text', 'markdown', 'url', 'pdf', 'event'
    source_url: Optional[str] = None
    external_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeSourceUrlCreate(BaseModel):
    """Payload for indexing a web page URL."""
    bot_id: str = "ems"
    url: str
    title: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeChunk(BaseModel):
    """A semantic chunk of knowledge with optional vector embedding."""
    id: Optional[UUID] = None
    bot_id: str = "ems"
    source_id: Optional[UUID] = None
    chunk_index: int = 0
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IngestionResult(BaseModel):
    """Result of an ingestion operation."""
    source_id: str
    title: str
    chunks_created: int
    status: str
    message: str


class SyncReport(BaseModel):
    """Report from an EMS synchronization run."""
    status: str
    total_events: int
    added_count: int
    updated_count: int
    deleted_count: int
    unchanged_count: int
    duration_ms: float
    error_log: Optional[str] = None
