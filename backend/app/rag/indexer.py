import hashlib
import io
from typing import Any, Dict, List, Optional
import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader

from app.core.config import settings
from app.core.logging import logger
from app.core.security import validate_ssrf_url
from app.models.event import EventKnowledge
from app.models.knowledge import IngestionResult, KnowledgeChunk
from app.rag.chunker import knowledge_chunker
from app.rag.embeddings import embedding_service
from app.services.supabase import supabase_service


class KnowledgeIndexer:
    """Indexing engine to convert events, documents, URLs, and PDFs into embedded RAG vectors."""

    def calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash to detect changes."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    async def index_event(self, event: EventKnowledge, bot_id: str = "ems") -> IngestionResult:
        """Index a single public EMS event."""
        # Check if already indexed with identical hash
        serialized_repr = event.model_dump_json()
        content_hash = self.calculate_hash(serialized_repr)

        existing_source = supabase_service.get_source_by_external_id(event.external_id, bot_id)
        if existing_source and existing_source.get("content_hash") == content_hash:
            logger.info(f"Event '{event.title}' is unchanged. Skipping re-indexing.")
            return IngestionResult(
                source_id=existing_source["id"],
                title=event.title,
                chunks_created=0,
                status="unchanged",
                message="Event content unchanged.",
            )

        # If updated, remove old chunks first
        if existing_source:
            supabase_service.delete_by_external_id(event.external_id, bot_id)

        # Generate semantic chunks
        chunks = knowledge_chunker.chunk_event(event, bot_id=bot_id)
        if not chunks:
            return IngestionResult(
                source_id="",
                title=event.title,
                chunks_created=0,
                status="failed",
                message="No chunks could be generated for event.",
            )

        # Generate vector embeddings
        chunk_texts = [c.content for c in chunks]
        embeddings = await embedding_service.get_batch_embeddings(chunk_texts)
        for i, emb in enumerate(embeddings):
            chunks[i].embedding = emb

        # Store in Supabase / Vector store
        source_id = await supabase_service.save_source_and_chunks(
            bot_id=bot_id,
            source_type="event",
            title=event.title,
            content_hash=content_hash,
            chunks=chunks,
            external_id=event.external_id,
            source_url=event.source_url,
            metadata={
                "event_id": event.external_id,
                "category": event.category,
                "date": event.date,
                "venue": event.venue,
                "organizer": event.organizer or event.club,
            },
        )

        logger.info(f"Successfully indexed event '{event.title}' with {len(chunks)} chunks.")
        return IngestionResult(
            source_id=source_id,
            title=event.title,
            chunks_created=len(chunks),
            status="ready",
            message=f"Indexed {len(chunks)} chunks successfully.",
        )

    async def index_url(self, url: str, title: Optional[str] = None, bot_id: str = "ems") -> IngestionResult:
        """Fetch and index public webpage text with SSRF protection."""
        validated_url = validate_ssrf_url(url)

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(validated_url, headers={"User-Agent": "EMS-Assistant-Bot/1.0"})
            response.raise_for_status()
            html_content = response.text

        soup = BeautifulSoup(html_content, "html.parser")
        # Strip script, style, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.decompose()

        page_title = title or (soup.title.string.strip() if soup.title else url)
        page_text = soup.get_text(separator="\n")
        # Clean multiple whitespaces
        cleaned_text = "\n".join([line.strip() for line in page_text.splitlines() if line.strip()])

        content_hash = self.calculate_hash(cleaned_text)
        chunks = knowledge_chunker.chunk_text(
            text=cleaned_text,
            title=page_title,
            source_type="url",
            bot_id=bot_id,
            extra_metadata={"url": url},
        )

        if not chunks:
            return IngestionResult(
                source_id="",
                title=page_title,
                chunks_created=0,
                status="failed",
                message="No extractable text found on page.",
            )

        chunk_texts = [c.content for c in chunks]
        embeddings = await embedding_service.get_batch_embeddings(chunk_texts)
        for i, emb in enumerate(embeddings):
            chunks[i].embedding = emb

        source_id = await supabase_service.save_source_and_chunks(
            bot_id=bot_id,
            source_type="url",
            title=page_title,
            content_hash=content_hash,
            chunks=chunks,
            source_url=url,
        )

        return IngestionResult(
            source_id=source_id,
            title=page_title,
            chunks_created=len(chunks),
            status="ready",
            message=f"Indexed webpage with {len(chunks)} chunks.",
        )

    async def index_pdf_bytes(
        self, pdf_bytes: bytes, filename: str, bot_id: str = "ems", extra_metadata: Dict[str, Any] = None
    ) -> IngestionResult:
        """Extract and index text from uploaded PDF documents."""
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            extracted_pages = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    extracted_pages.append(f"[Page {i+1}]\n{page_text}")

            full_text = "\n\n".join(extracted_pages).strip()
            if not full_text:
                return IngestionResult(
                    source_id="",
                    title=filename,
                    chunks_created=0,
                    status="failed",
                    message="No text could be extracted from PDF.",
                )

            content_hash = self.calculate_hash(full_text)
            chunks = knowledge_chunker.chunk_text(
                text=full_text,
                title=filename,
                source_type="pdf",
                bot_id=bot_id,
                extra_metadata=extra_metadata or {},
            )

            chunk_texts = [c.content for c in chunks]
            embeddings = await embedding_service.get_batch_embeddings(chunk_texts)
            for i, emb in enumerate(embeddings):
                chunks[i].embedding = emb

            source_id = await supabase_service.save_source_and_chunks(
                bot_id=bot_id,
                source_type="pdf",
                title=filename,
                content_hash=content_hash,
                chunks=chunks,
                metadata=extra_metadata,
            )

            return IngestionResult(
                source_id=source_id,
                title=filename,
                chunks_created=len(chunks),
                status="ready",
                message=f"Successfully indexed PDF with {len(chunks)} chunks.",
            )
        except Exception as e:
            logger.error(f"PDF indexing error for {filename}: {e}")
            return IngestionResult(
                source_id="",
                title=filename,
                chunks_created=0,
                status="failed",
                message=f"PDF extraction error: {str(e)}",
            )


knowledge_indexer = KnowledgeIndexer()
