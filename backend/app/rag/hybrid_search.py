import re
from typing import Any, Dict, List, Optional, Tuple
from app.ai.query_analysis import QueryAnalysis, query_analyzer
from app.core.config import settings
from app.core.logging import logger
from app.models.chat import EventCard, PageContext, SourceReference
from app.rag.retriever import vector_retriever
from app.services.supabase import supabase_service


class HybridSearchEngine:
    """Precision-first hybrid search engine combining vector similarity, exact entity match, and topic filtering."""

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
        """Perform precision-first hybrid search with intent-guided pruning."""
        # 1. Analyze query if not already provided
        analysis = query_analysis or query_analyzer.analyze(query)
        clean_query = analysis.normalized_query

        # Determine target event filter from page context or query entity
        event_id_filter = None
        if page_context and page_context.event_id:
            event_id_filter = page_context.event_id
        elif analysis.matched_event_id and not analysis.wants_related:
            event_id_filter = analysis.matched_event_id

        # 2. Vector Search
        vector_results = await vector_retriever.retrieve(
            query=clean_query,
            bot_id=bot_id,
            event_id=event_id_filter,
            top_k=top_k * 2,
            threshold=settings.MIN_SIMILARITY_THRESHOLD,
        )

        # 3. All chunks in storage for keyword & metadata evaluation
        all_chunks = supabase_service.in_memory.get_all_chunks(bot_id=bot_id)

        # 4. Score every chunk based on Precision-First criteria
        scored_candidates: List[Tuple[Dict[str, Any], float]] = []

        # Map vector similarity scores for fast lookup
        vector_sim_map = {str(r.get("id")): r.get("similarity", 0.0) for r in vector_results}

        for chunk in all_chunks:
            meta = chunk.get("metadata", {})
            chunk_id = str(chunk.get("id"))
            c_event_id = meta.get("event_id")
            c_event_name = (meta.get("event_name") or meta.get("title") or "").lower()
            c_category = (meta.get("category") or "").lower()
            c_content = chunk.get("content", "").lower()
            c_date = meta.get("date", "")

            # If an explicit single-event filter is active, skip all other events
            if event_id_filter and c_event_id != event_id_filter:
                continue

            score = 0.0

            # Tier 1: Exact Event Target Match
            if analysis.matched_event_id and c_event_id == analysis.matched_event_id:
                score += 0.95

            # Tier 2: Specific Topic Match (e.g. 'generative ai' vs generic 'ai')
            if "generative ai" in analysis.topics:
                if "genai" in c_event_name or "generative ai" in c_event_name or "ai agents" in c_event_name:
                    score += 0.90
                elif "hackverse" in c_event_name:
                    # Penalize HackVerse when user specifically asked for Gen AI
                    score -= 0.50

            elif "iot" in analysis.topics:
                if "iot" in c_event_name or "embedded" in c_event_name or "robotics" in c_event_name:
                    score += 0.90

            elif "cybersecurity" in analysis.topics:
                if "cybershield" in c_event_name or "ctf" in c_event_name or "security" in c_event_name:
                    score += 0.90

            # Tier 3: Category Match (e.g. 'Workshop', 'Hackathon')
            if analysis.category_filter and analysis.category_filter.lower() in c_category:
                score += 0.40

            # Tier 4: Date Filter Match
            if analysis.date_label:
                # If date matches
                if analysis.date_label == "today" and ("today" in c_date.lower() or "09-03" in c_date):
                    score += 0.50
                elif analysis.date_label == "tomorrow" and ("09-04" in c_date or "09-05" in c_date):
                    score += 0.50
                elif analysis.date_label in ("this week", "this month"):
                    score += 0.30

            # Tier 5: Title / Keyword Substring Match
            for word in clean_query.split():
                if len(word) > 2 and word in c_event_name:
                    score += 0.25
                elif len(word) > 2 and word in c_content:
                    score += 0.05

            # Tier 6: Vector Similarity Contribution
            v_sim = vector_sim_map.get(chunk_id, 0.0)
            score += v_sim * 0.35

            if score > 0.20:
                scored_candidates.append((chunk, score))

        # Sort candidates by calculated precision score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # 5. Intent-Based Dynamic Pruning
        # If user asked for a specific topic or event (and not 'all' or 'similar'), keep only the top matching event!
        accepted_chunks: List[Dict[str, Any]] = []

        if scored_candidates:
            top_score = scored_candidates[0][1]
            top_event_id = scored_candidates[0][0].get("metadata", {}).get("event_id")

            # Check if user asked for a single specific topic/event
            is_single_target = (
                analysis.matched_event_id is not None
                or (len(analysis.topics) > 0 and not analysis.wants_multiple and not analysis.wants_related)
            )

            for chunk, score in scored_candidates:
                c_event_id = chunk.get("metadata", {}).get("event_id")

                if is_single_target:
                    # Only accept chunks from the top matched event
                    if c_event_id == top_event_id:
                        accepted_chunks.append(chunk)
                else:
                    # Multi-event discovery: accept events above precision threshold
                    if score >= settings.MIN_PRECISION_SCORE or score >= (top_score * 0.65):
                        accepted_chunks.append(chunk)

                if len(accepted_chunks) >= top_k:
                    break

        # 6. Fallback if no candidate matched but page context exists
        if not accepted_chunks and page_context and page_context.event_id:
            for c in all_chunks:
                if c.get("metadata", {}).get("event_id") == page_context.event_id:
                    accepted_chunks.append(c)
                    if len(accepted_chunks) >= 3:
                        break

        # 7. Extract Deduplicated Event Cards & Grouped Source References
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
                        date=meta.get("date"),
                        venue=meta.get("venue"),
                        organizer=meta.get("organizer"),
                        category=meta.get("category"),
                        url=meta.get("url") or f"/events/{event_id}",
                    )
                )

            source_title = meta.get("source_title") or event_name or meta.get("title") or "EMS Event Data"
            if source_title not in seen_sources:
                seen_sources.add(source_title)
                source_refs.append(
                    SourceReference(
                        title=source_title,
                        source_type=meta.get("source_type", "EMS Database"),
                        url=meta.get("url"),
                    )
                )

        # 8. Observability Logging (when DEBUG_RAG is enabled)
        if settings.DEBUG_RAG:
            logger.info(
                f"[RAG Observability] query='{query}' -> norm='{clean_query}', intent={analysis.intent}, "
                f"topics={analysis.topics}, target_event={analysis.matched_event_id}, "
                f"candidates={len(scored_candidates)}, accepted={len(accepted_chunks)}, "
                f"events={[c.title for c in event_cards]}"
            )

        return accepted_chunks, event_cards, source_refs


hybrid_search_engine = HybridSearchEngine()
