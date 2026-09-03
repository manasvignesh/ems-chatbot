import uuid
from typing import List, Optional
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel

from app.core.logging import logger
from app.models.knowledge import IngestionResult, KnowledgeChunk, KnowledgeSourceCreate, KnowledgeSourceUrlCreate
from app.rag.chunker import knowledge_chunker
from app.rag.embeddings import embedding_service
from app.rag.indexer import knowledge_indexer
from app.services.supabase import supabase_service

router = APIRouter(prefix="/knowledge", tags=["Knowledge Ingestion"])


@router.post("/text", response_model=IngestionResult)
async def index_text_content(payload: KnowledgeSourceCreate):
    """Index raw text or markdown document into vector knowledge."""
    if not payload.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty.")

    content_hash = knowledge_indexer.calculate_hash(payload.content)
    chunks = knowledge_chunker.chunk_text(
        text=payload.content,
        title=payload.title,
        source_type=payload.source_type,
        bot_id=payload.bot_id,
        extra_metadata=payload.metadata,
    )

    if not chunks:
        raise HTTPException(status_code=400, detail="Could not produce chunks from content.")

    # Embed and save
    chunk_texts = [c.content for c in chunks]
    embeddings = await embedding_service.get_batch_embeddings(chunk_texts)
    for i, emb in enumerate(embeddings):
        chunks[i].embedding = emb

    source_id = await supabase_service.save_source_and_chunks(
        bot_id=payload.bot_id,
        source_type=payload.source_type,
        title=payload.title,
        content_hash=content_hash,
        chunks=chunks,
        external_id=payload.external_id,
        source_url=payload.source_url,
        metadata=payload.metadata,
    )

    return IngestionResult(
        source_id=source_id,
        title=payload.title,
        chunks_created=len(chunks),
        status="ready",
        message="Text indexed successfully.",
    )


@router.post("/url", response_model=IngestionResult)
async def index_web_url(payload: KnowledgeSourceUrlCreate):
    """Index public webpage content safely with SSRF protection."""
    try:
        return await knowledge_indexer.index_url(
            url=payload.url,
            title=payload.title,
            bot_id=payload.bot_id,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"URL indexing error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to index URL: {str(e)}")


@router.post("/file", response_model=IngestionResult)
async def index_uploaded_pdf(
    file: UploadFile = File(...),
    bot_id: str = Query("ems"),
    title: Optional[str] = Query(None),
):
    """Upload and index PDF event attachments or rulebooks."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="PDF file size exceeds 10MB limit.")

    doc_title = title or file.filename
    return await knowledge_indexer.index_pdf_bytes(
        pdf_bytes=pdf_bytes,
        filename=doc_title,
        bot_id=bot_id,
        extra_metadata={"filename": file.filename},
    )


@router.delete("/{source_id}")
async def delete_knowledge_source(source_id: str):
    """Delete a knowledge source and all its associated chunks."""
    supabase_service.delete_source(source_id)
    return {"status": "success", "message": f"Deleted knowledge source {source_id}."}
