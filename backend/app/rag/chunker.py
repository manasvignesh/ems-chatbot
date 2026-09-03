import re
from typing import Any, Dict, List
from app.models.event import EventKnowledge
from app.models.knowledge import KnowledgeChunk


class KnowledgeChunker:
    """Semantic chunking strategies for EMS events and text documents."""

    def chunk_event(self, event: EventKnowledge, bot_id: str = "ems") -> List[KnowledgeChunk]:
        """Generate focused, high-relevance semantic chunks for an EMS event."""
        chunks: List[KnowledgeChunk] = []
        chunk_idx = 0

        # Base metadata shared across all chunks for this event
        base_meta = {
            "event_id": event.external_id,
            "event_name": event.title,
            "category": event.category,
            "venue": event.venue,
            "date": event.date,
            "organizer": event.organizer or event.club,
            "url": event.source_url,
            "registration_deadline": event.registration_deadline,
            "team_size": event.team_size,
            "eligibility": event.eligibility,
        }

        # 1. EVENT OVERVIEW CHUNK
        overview_parts = [
            f"EVENT: {event.title}",
            f"Category: {event.category or 'General'}",
            f"Organizer / Club: {event.organizer or event.club or 'MLRIT CIE'}",
        ]
        if event.date:
            overview_parts.append(f"Date: {event.date}")
        if event.start_time or event.end_time:
            overview_parts.append(f"Timings: {event.start_time or ''} to {event.end_time or ''}".strip())
        if event.venue:
            overview_parts.append(f"Venue: {event.venue}")
        if event.description:
            overview_parts.append(f"Overview: {event.description[:400]}")

        chunks.append(
            KnowledgeChunk(
                bot_id=bot_id,
                chunk_index=chunk_idx,
                content="\n".join(overview_parts),
                metadata={
                    **base_meta,
                    "section": "overview",
                },
            )
        )
        chunk_idx += 1

        # 2. REGISTRATION & ELIGIBILITY CHUNK
        reg_parts = [
            f"EVENT: {event.title} - REGISTRATION, ELIGIBILITY & TEAM SIZE",
            f"Registration Deadline: {event.registration_deadline or 'Check event page'}",
            f"Eligibility: {event.eligibility or 'Open to all students'}",
            f"Team Size: {event.team_size or 'Individual or team'}",
        ]
        if event.prizes:
            reg_parts.append(f"Prizes & Perks: {event.prizes}")

        chunks.append(
            KnowledgeChunk(
                bot_id=bot_id,
                chunk_index=chunk_idx,
                content="\n".join(reg_parts),
                metadata={
                    **base_meta,
                    "section": "registration",
                },
            )
        )
        chunk_idx += 1

        # 3. SCHEDULE & VENUE CHUNK
        if event.schedule or event.venue or event.start_time:
            sched_parts = [
                f"EVENT: {event.title} - SCHEDULE, VENUE & TIMINGS",
                f"Date: {event.date or 'TBA'}",
                f"Timings: {event.start_time or 'TBA'} - {event.end_time or 'TBA'}",
                f"Venue: {event.venue or 'TBA'}",
            ]
            if event.schedule:
                sched_parts.append(f"Detailed Schedule:\n{event.schedule}")

            chunks.append(
                KnowledgeChunk(
                    bot_id=bot_id,
                    chunk_index=chunk_idx,
                    content="\n".join(sched_parts),
                    metadata={
                        **base_meta,
                        "section": "schedule",
                    },
                )
            )
            chunk_idx += 1

        # 4. RULES & REQUIREMENTS CHUNK
        if event.rules or event.requirements:
            rules_parts = [f"EVENT: {event.title} - RULES & REQUIREMENTS"]
            if event.rules:
                rules_parts.append("Official Rules:")
                for r in event.rules:
                    rules_parts.append(f"- {r}")
            if event.requirements:
                rules_parts.append("Requirements & What to Bring:")
                for req in event.requirements:
                    rules_parts.append(f"- {req}")

            chunks.append(
                KnowledgeChunk(
                    bot_id=bot_id,
                    chunk_index=chunk_idx,
                    content="\n".join(rules_parts),
                    metadata={
                        **base_meta,
                        "section": "rules",
                    },
                )
            )
            chunk_idx += 1

        # 5. FULL DESCRIPTION CHUNK
        if event.description and len(event.description) > 400:
            chunks.append(
                KnowledgeChunk(
                    bot_id=bot_id,
                    chunk_index=chunk_idx,
                    content=f"EVENT: {event.title} - DETAILED DESCRIPTION\n{event.description}",
                    metadata={
                        **base_meta,
                        "section": "description",
                    },
                )
            )
            chunk_idx += 1

        return chunks

    def chunk_text(
        self,
        text: str,
        title: str,
        source_type: str = "text",
        bot_id: str = "ems",
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        extra_metadata: Dict[str, Any] = None,
    ) -> List[KnowledgeChunk]:
        """Split arbitrary document text into overlapping semantic chunks."""
        extra_metadata = extra_metadata or {}
        chunks: List[KnowledgeChunk] = []

        # Clean text
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            return []

        # Split by paragraphs or double newlines where possible
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        current_chunk_words: List[str] = []
        current_len = 0
        chunk_idx = 0

        for para in paragraphs:
            para_words = para.split()
            if current_len + len(para_words) > chunk_size and current_chunk_words:
                chunk_text = f"DOCUMENT: {title}\n" + " ".join(current_chunk_words)
                chunks.append(
                    KnowledgeChunk(
                        bot_id=bot_id,
                        chunk_index=chunk_idx,
                        content=chunk_text,
                        metadata={
                            "title": title,
                            "source_type": source_type,
                            "chunk_index": chunk_idx,
                            **extra_metadata,
                        },
                    )
                )
                chunk_idx += 1
                # Retain overlap
                current_chunk_words = current_chunk_words[-chunk_overlap:]
                current_len = len(current_chunk_words)

            current_chunk_words.extend(para_words)
            current_len += len(para_words)

        if current_chunk_words:
            chunk_text = f"DOCUMENT: {title}\n" + " ".join(current_chunk_words)
            chunks.append(
                KnowledgeChunk(
                    bot_id=bot_id,
                    chunk_index=chunk_idx,
                    content=chunk_text,
                    metadata={
                        "title": title,
                        "source_type": source_type,
                        "chunk_index": chunk_idx,
                        **extra_metadata,
                    },
                )
            )

        return chunks


knowledge_chunker = KnowledgeChunker()
