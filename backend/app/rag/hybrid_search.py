import re
from typing import Any, Dict, List, Optional, Tuple
from app.ai.query_analysis import QueryAnalysis, query_analyzer
from app.core.config import settings
from app.core.logging import logger
from app.models.chat import EventCard, PageContext, SourceReference
from app.rag.retriever import vector_retriever
from app.services.supabase import supabase_service


class HybridSearchEngine:
    """Precision-first hybrid search engine combining vector similarity, exact entity match, and Equinox topic filtering."""

    def __init__(self):
        self.rrf_k = 60

    async def search(
        self,
        query: str,
        bot_id: str = "ems",
        page_context: Optional[PageContext] = None,
        query_analysis: Optional[QueryAnalysis] = None,
        top_k: int = 6,
    ) -> Tuple[List[Dict[str, Any]], List[EventCard], List[SourceReference]]:
        """Perform precision-first hybrid search for Equinox 2.0 with intent-guided pruning."""
        analysis = query_analysis or query_analyzer.analyze(query)
        clean_query = analysis.normalized_query

        # Determine target event filter from page context or query entity
        event_id_filter = None
        if page_context and page_context.event_id:
            event_id_filter = page_context.event_id
        elif analysis.matched_event_id and not analysis.wants_related:
            event_id_filter = analysis.matched_event_id

        # 1. Vector Search
        vector_results = await vector_retriever.retrieve(
            query=clean_query,
            bot_id=bot_id,
            event_id=event_id_filter,
            top_k=top_k * 2,
            threshold=settings.MIN_SIMILARITY_THRESHOLD,
        )

        # 2. All chunks in storage for keyword & metadata evaluation
        all_chunks = supabase_service.in_memory.get_all_chunks(bot_id=bot_id)

        # 3. Score every chunk based on Equinox Precision-First criteria
        scored_candidates: List[Tuple[Dict[str, Any], float]] = []
        vector_sim_map = {str(r.get("id")): r.get("similarity", 0.0) for r in vector_results}

        for chunk in all_chunks:
            meta = chunk.get("metadata", {})
            chunk_id = str(chunk.get("id"))
            c_event_id = meta.get("event_id")
            c_event_name = (meta.get("event_name") or meta.get("title") or "").lower()
            c_content = chunk.get("content", "").lower()
            c_section = meta.get("section", "").lower()

            # If explicit single-event target is set, skip other events
            if event_id_filter and c_event_id != event_id_filter:
                continue

            score = 0.0

            # Tier 1: Target Sub-event Match
            if analysis.matched_event_id and c_event_id == analysis.matched_event_id:
                score += 0.95

            # Tier 2: Sponsorship match
            if "sponsorship" in analysis.topics and ("sponsor" in c_content or "sponsorship" in c_section):
                score += 0.90

            # Tier 3: Contact / Address match
            if "contact" in analysis.topics and ("contact" in c_content or "cie@mlrinstitutions.ac.in" in c_content or "coordinators" in c_content):
                score += 0.90

            # Tier 4: CIE Background match
            if "cie" in analysis.topics and ("established in 2015" in c_content or "metaloop" in c_content or "inventron" in c_content):
                score += 0.90

            # Tier 5: Sub-events listing query
            if analysis.wants_multiple and ("10 flagship sub-events" in c_content or "sub_event" in c_section or "activities" in c_content):
                score += 0.85

            # Tier 6: Keyword overlap
            for word in clean_query.split():
                if len(word) > 2:
                    if word in c_event_name:
                        score += 0.30
                    elif word in c_content:
                        score += 0.08

            # Tier 7: Vector Similarity
            v_sim = vector_sim_map.get(chunk_id, 0.0)
            score += v_sim * 0.35

            if score > 0.20:
                scored_candidates.append((chunk, score))

        # Sort candidates
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # Dynamic Pruning
        accepted_chunks: List[Dict[str, Any]] = []
        if scored_candidates:
            top_score = scored_candidates[0][1]
            top_event_id = scored_candidates[0][0].get("metadata", {}).get("event_id")

            is_single_target = (
                analysis.matched_event_id is not None
                and not analysis.wants_multiple
                and not analysis.wants_related
            )

            for chunk, score in scored_candidates:
                c_event_id = chunk.get("metadata", {}).get("event_id")

                if is_single_target:
                    if c_event_id == top_event_id:
                        accepted_chunks.append(chunk)
                else:
                    if score >= settings.MIN_PRECISION_SCORE or score >= (top_score * 0.60):
                        accepted_chunks.append(chunk)

                if len(accepted_chunks) >= top_k:
                    break

        # Extract Event Cards & Sources
        event_cards: List[EventCard] = []
        source_refs: List[SourceReference] = []
        seen_events = set()
        seen_sources = set()

        for chunk in accepted_chunks:
            meta = chunk.get("metadata", {})
            event_id = meta.get("event_id")
            event_name = meta.get("event_name") or meta.get("title")

            if event_id and event_name and event_id not in seen_events:
                seen_events.add(event_id)
                event_cards.append(
                    EventCard(
                        event_id=event_id,
                        title=event_name,
                        date=meta.get("date", "30–31 October"),
                        venue=meta.get("venue", "MLR Institute of Technology, Hyderabad"),
                        organizer=meta.get("organizer", "MLRIT CIE"),
                        category=meta.get("category", "E-Summit"),
                        url=meta.get("url") or f"/events/{event_id}",
                    )
                )

            source_title = meta.get("source_title") or event_name or meta.get("title") or "The Equinox 2.0"
            if source_title not in seen_sources:
                seen_sources.add(source_title)
                source_refs.append(
                    SourceReference(
                        title=source_title,
                        source_type=meta.get("source_type", "Equinox Brochure / Prospectus"),
                        url=meta.get("url"),
                    )
                )

        if settings.DEBUG_RAG:
            logger.info(
                f"[RAG Observability] query='{query}' -> target_event={analysis.matched_event_id}, "
                f"candidates={len(scored_candidates)}, accepted={len(accepted_chunks)}, "
                f"events={[c.title for c in event_cards]}"
            )

        return accepted_chunks, event_cards, source_refs


hybrid_search_engine = HybridSearchEngine()
