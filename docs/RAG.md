# Retrieval-Augmented Generation (RAG) Architecture for The Equinox 2.0

This document details the knowledge chunking, vector embedding, hybrid precision search, precomputed FAQ layer, typo normalization, and temporal synchronization powering **The Equinox 2.0 Assistant**.

---

## 1. Query Understanding & Typo Tolerance Pipeline

Before retrieval, incoming user queries pass through the **Structured Query Analyzer**:

```
User Query: "ipl action bidding"
      ↓
[1. Case & Whitespace Normalization]
      ↓
[2. Domain Typo & Alias Correction]
    - "ipl action" -> "ipl auction"
      ↓
[3. Relative Temporal Range Parsing]
    - "today", "tomorrow", "this week", "this weekend", "this month"
    - Resolved in Asia/Kolkata timezone
      ↓
[4. Fuzzy Entity & Title Matcher (RapidFuzz)]
    - Fuzzy match against known Equinox sub-events (Spotlight, Crossroads, Startup Expo, Brand Battles, IPL Auction, Hustle Mania, Internship Drive, Startup Poly, E-Cell Meet, Pitch Deck)
      ↓
QueryAnalysis Object:
{
  "original_query": "ipl action bidding",
  "normalized_query": "ipl auction bidding",
  "intent": "SPECIFIC_EVENT",
  "topics": ["sub_events"],
  "matched_event_id": "ipl-auction"
}
```

---

## 2. Fast Preloaded Conversation & FAQ Layer (Bypassing Gemini)

Most expected Equinox questions do not incur LLM token usage or latency:

1. **Small-Talk Layer**:
   - Greetings (`"hello"`, `"hi"`, `"good morning"`)
   - Gratitude (`"thanks"`, `"thank you"`)
   - Identity & Capabilities (`"who are you"`, `"what can you do"`, `"help"`)

2. **Precomputed Verified Equinox FAQ Matcher**:
   - 60+ categorized FAQ clusters with extensive question variants.
   - High-confidence exact, fuzzy (`fuzz.token_sort_ratio`), and keyword semantic matching.
   - Answers returned instantly in `< 1ms` with **0 Gemini calls**.

---

## 3. Authoritative Time & Date Context

- Authoritative dates for The Equinox 2.0 are **30–31 October** at **MLR Institute of Technology, Hyderabad**.
- The year is not inferred or invented.
- If information is missing from the authoritative documents, the chatbot states:
  *"That information is not available in the current Equinox information."*

---

## 4. Precision-First Retrieval & Context Pruning

### Resolving Sub-Event Precision (e.g., "Monopoly" vs "Startup Poly")
The system employs **Hierarchical Precision Scoring**:
1. **Tier 1 (1.00)**: Exact Sub-Event Match (`Startup Poly`, `IPL Auction`, `Spotlight`, etc.).
2. **Tier 2 (0.90)**: Sponsorship / Contact / CIE topic match.
3. **Tier 3 (0.85)**: Multi-event listing match.
4. **Tier 4**: BM25 keyword matching and dense vector similarity.

Dynamic Top-K pruning drops distant candidates, preventing noise from reaching generation.
