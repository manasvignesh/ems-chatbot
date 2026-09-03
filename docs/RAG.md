# Retrieval-Augmented Generation (RAG) Architecture

This document details the knowledge chunking, vector embedding, hybrid precision search, typo normalization, and timezone-aware temporal synchronization powering **EMS Assistant**.

---

## 1. Query Understanding & Typo Tolerance Pipeline

Before retrieval, incoming user queries pass through the **Structured Query Analyzer**:

```
User Query: "genarative ai workshp"
      ↓
[1. Case & Whitespace Normalization]
      ↓
[2. Domain Typo & Alias Correction]
    - "genarative ai" -> "generative ai"
    - "workshp"       -> "workshop"
      ↓
[3. Relative Temporal Range Parsing]
    - "today", "tomorrow", "this week", "this weekend", "this month"
    - Resolved in Asia/Kolkata timezone
      ↓
[4. Fuzzy Entity & Title Matcher (RapidFuzz)]
    - Fuzzy match against known event titles and aliases (threshold >= 80)
      ↓
QueryAnalysis Object:
{
  "original_query": "genarative ai workshp",
  "normalized_query": "generative ai workshop",
  "intent": "TOPIC_SEARCH",
  "topics": ["generative ai"],
  "category_filter": "Workshop",
  "matched_event_id": "ai-agents-bootcamp"
}
```

---

## 2. Fast Preloaded Conversation Layer (Bypassing RAG)

Common small-talk queries do not incur latency, embedding costs, or LLM token usage:

- **Greetings**: `"hello"`, `"hi"`, `"hey"`, `"hii"`, `"good morning"`, `"good afternoon"`, `"good evening"`
- **Gratitude**: `"thanks"`, `"thank you"`, `"thanks bro"`, `"thx"`
- **Farewells**: `"bye"`, `"goodbye"`, `"see you"`
- **Identity & Capabilities**: `"who are you"`, `"what can you do"`, `"help"`

> **Mixed Query Guarantee**: Messages combining small-talk and an actual question (e.g., *"hello, what events are today?"*) automatically pass through to the full precision RAG pipeline.

---

## 3. Authoritative Time & Date Context

To prevent Gemini from hallucinating dates or guessing the current year:
1. The server computes the authoritative current time in `Asia/Kolkata` (`settings.EMS_TIMEZONE`).
2. Relative date queries (`"tomorrow"`, `"this weekend"`, `"next week"`) are parsed in Python before retrieval.
3. Every prompt sent to Gemini includes the authoritative time context:
   ```
   [CURRENT AUTHORITATIVE TIME CONTEXT]
   Current Date: 2026-09-03 (Thursday)
   Current Local Time: 10:15 PM (Asia/Kolkata)
   Current Year: 2026, Month: September
   All event dates and schedules are relative to this current time.
   ```

---

## 4. Precision-First Retrieval & Context Pruning

### Resolving Over-Broad Retrieval ("Gen AI" vs "HackVerse")
In traditional naive vector search, a query for `"gen ai"` might return `HackVerse` merely because HackVerse mentions AI in passing.

EMS Assistant eliminates over-broad retrieval through **Hierarchical Precision Scoring**:
1. **Tier 1 (1.00)**: Exact Event Title or Matched ID Match.
2. **Tier 2 (0.95)**: Specific Topic Match (e.g. `"generative ai"` explicitly matching `Autonomous AI Agents & GenAI Bootcamp`). HackVerse receives a penalty ($-0.50$) if it only mentions generic AI.
3. **Tier 3 (0.80)**: Category Match (`Workshop`, `Hackathon`).
4. **Tier 4 (0.90)**: Target Date Filter Match.
5. **Tier 5**: BM25 keyword matching and dense vector similarity.

### Dynamic Top-K & Context Pruning
- If the top result has a strong specific score ($\ge 0.85$), all weak or distant candidates are pruned.
- Chunks are grouped by `event_id` and deduplicated so each event appears once.
- Gemini is explicitly instructed to answer only what the user asked and never introduce unrelated events from context.

---

## 5. Chunking Strategy

For every public EMS event, the indexer creates distinct, focused chunks:

| Section | Content | Target Queries |
| :--- | :--- | :--- |
| **Overview** | Event title, organizer, category, summary, date, venue | *"What is HackVerse?", "Any workshops organized by RIoT Club?"* |
| **Registration** | Registration deadlines, fees, eligibility criteria, team size, prizes | *"What is the registration deadline?", "Can first years participate?", "What is the team size?"* |
| **Schedule** | Timelines, agendas, start/end hours, specific rooms/labs | *"When does it start?", "What is the schedule for Day 2?", "Where is Room 214?"* |
| **Rules & Requirements** | Official guidelines, software/hardware prerequisites, what to bring | *"What are the rules?", "Do I need to bring a laptop?", "Is pre-built code allowed?"* |
| **Description** | Full narrative description & background | In-depth context on problem statements and topics |
