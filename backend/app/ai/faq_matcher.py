import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple
from rapidfuzz import fuzz

from app.core.logging import logger

FAQ_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge", "equinox_faq.json")


class EquinoxFAQMatcher:
    """Fast deterministic matcher for precomputed Equinox 2.0 FAQs."""

    def __init__(self, faq_path: str = FAQ_FILE_PATH):
        self.faq_path = faq_path
        self.faqs: List[Dict[str, Any]] = []
        self._load_faqs()

    def _load_faqs(self):
        try:
            if os.path.exists(self.faq_path):
                with open(self.faq_path, "r", encoding="utf-8") as f:
                    self.faqs = json.load(f)
                logger.info(f"Loaded {len(self.faqs)} Equinox FAQs successfully.")
            else:
                logger.warning(f"FAQ file not found at {self.faq_path}")
        except Exception as e:
            logger.error(f"Error loading Equinox FAQs: {e}")

    def clean_text(self, text: str) -> str:
        """Strip punctuation and extra whitespace for clean matching."""
        lower = text.lower().strip()
        cleaned = re.sub(r"[^\w\s]", " ", lower)
        return " ".join(cleaned.split())

    def match(self, query: str) -> Tuple[Optional[Dict[str, Any]], str, float]:
        """
        Match user query against Equinox FAQs.
        Returns: (matched_faq, answer_mode, confidence_score)
        answer_mode: 'FAQ_EXACT' | 'FAQ_FUZZY' | 'FAQ_SEMANTIC' | 'NONE'
        """
        if not self.faqs or not query.strip():
            return None, "NONE", 0.0

        clean_q = self.clean_text(query)
        words_q = set(clean_q.split())

        best_faq = None
        best_score = 0.0
        best_mode = "NONE"

        # 1. Check exact match across canonical and all variants first
        for faq in self.faqs:
            canonical = self.clean_text(faq["canonical_question"])
            variants = [self.clean_text(v) for v in faq.get("question_variants", [])]

            if clean_q == canonical or clean_q in variants:
                return faq, "FAQ_EXACT", 1.0

        # 2. Check specific topic keywords priority (e.g. fee, deadline, prize, year, dates, venue, contacts)
        for faq in self.faqs:
            keywords = [k.lower() for k in faq.get("keywords", [])]
            # If all strong keywords present
            strong_matches = [k for k in keywords if len(k) > 3 and (k in clean_q or f" {k} " in f" {clean_q} ")]
            if len(strong_matches) >= 2:
                kw_score = 0.85 + (min(len(strong_matches), 3) * 0.04)
                if kw_score > best_score:
                    best_score = kw_score
                    best_faq = faq
                    best_mode = "FAQ_SEMANTIC"

        # 3. Fuzzy similarity using token_sort_ratio and weighted ratio (prevents subset explosion)
        for faq in self.faqs:
            canonical = self.clean_text(faq["canonical_question"])
            variants = [self.clean_text(v) for v in faq.get("question_variants", [])]

            for variant in [canonical] + variants:
                sort_ratio = fuzz.token_sort_ratio(clean_q, variant)
                w_ratio = fuzz.WRatio(clean_q, variant)
                combined_ratio = (sort_ratio * 0.6) + (w_ratio * 0.4)

                if combined_ratio >= 78 and (combined_ratio / 100.0) > best_score:
                    best_score = combined_ratio / 100.0
                    best_faq = faq
                    best_mode = "FAQ_FUZZY"

        if best_faq and best_score >= 0.75:
            return best_faq, best_mode, best_score

        return None, "NONE", 0.0


faq_matcher = EquinoxFAQMatcher()
