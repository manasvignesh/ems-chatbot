# System Architecture: EMS Assistant

EMS Assistant is a production-grade, standalone AI Event Assistant built specifically for the MLRIT CIE Event Management System (EMS). It provides intelligent, grounded event discovery and participation guidance through a decoupled, embeddable architecture.

---

## 1. High-Level System Architecture

```mermaid
graph TD
    subgraph Host["EMS Target Website (Next.js / HTML)"]
        Site[EMS Web Pages] -->|Injects Script| WidgetScript["widget.js"]
    end

    subgraph ClientLayer["Client-Side Widget (Shadow DOM)"]
        WidgetScript --> ShadowRoot["Shadow Root #shadow-root"]
        ShadowRoot --> Launcher["Floating 'Ask EMS' Launcher"]
        ShadowRoot --> ChatPanel["Chat Panel UI"]
        ChatPanel --> BodyOverlay["10s Error Spam Portal (Mounted on document.body)"]
    end

    subgraph BackendLayer["Python FastAPI Backend Service"]
        ChatPanel -->|HTTPS REST API /api/chat| APIRouter["FastAPI App"]
        APIRouter --> RateLimit["IP & Session Rate Limiter"]
        APIRouter --> Classifier["Layered Scope Classifier"]
        Classifier -->|OUT_OF_SCOPE| OutOfScopeResp["{status: 'out_of_scope', cooldown_seconds: 10}"]
        Classifier -->|IN_SCOPE| MemoryMgr["Conversational Memory & Pronoun Resolver"]
        MemoryMgr --> HybridSearch["Hybrid Search Engine (RRF)"]
        HybridSearch --> VectorRetriever["Vector Similarity (pgvector)"]
        HybridSearch --> KeywordSearch["BM25 / Exact Entity Matcher"]
        HybridSearch --> PromptBuilder["Guarded Prompt Builder"]
        PromptBuilder --> GeminiEngine["Google Gemini 2.5 Flash"]
    end

    subgraph DataStorage["Data & Ingestion Layer"]
        GeminiEngine -->|Text Embeddings| GoogleGenAI["text-embedding-004"]
        VectorRetriever --> SupabaseDB[("Supabase PostgreSQL + pgvector")]
        EMSConnector["EMS Public Connector"] -->|Sync Pipeline| Indexer["Knowledge Indexer (SHA256)"]
        Indexer --> SupabaseDB
    end
```

---

## 2. Key Architectural Tenets

1. **Zero Coupling to EMS Source Tree**:
   - The chatbot runs as an autonomous service on its own server/container.
   - Host integration requires only one standard `<script src="https://.../widget.js">` tag.
   - Completely independent deployment and scaling cycles.

2. **Shadow DOM Style Isolation**:
   - The entire widget UI (buttons, panels, cards, inputs, scrollbars) is encapsulated within an open Shadow Root.
   - Host website CSS (Tailwind, Bootstrap, or custom stylesheets) can never bleed into or break the chatbot UI.
   - Chatbot styles cannot affect any host website layout.

3. **Grounded RAG Factuality Guarantee**:
   - Event-specific facts (dates, venues, deadlines, fees, rules, team sizes, eligibility) are drawn exclusively from retrieved EMS knowledge chunks.
   - Gemini is strictly forbidden from fabricating event attributes.
   - Missing attributes trigger a clear statement: *"I couldn't find that specific information in the current EMS data."*

4. **Multi-Layered Scope & Injection Guardrails**:
   - **Layer 1: Heuristic Filter & Injection Detector**: Evaluates SQL patterns, system prompt extraction strings, and overt off-topic triggers.
   - **Layer 2: Page Context & Conversational Context**: Preserves continuity when users ask context-dependent questions (*"What is the team size?"* or *"Where is it?"*).
   - **Layer 3: Structured Gemini JSON Classifier**: For ambiguous inputs, invokes Gemini in strict JSON mode to classify as `IN_SCOPE`, `AMBIGUOUS`, or `OUT_OF_SCOPE`.

5. **10-Second Intentional Error Spam Effect**:
   - When an out-of-scope query is verified, the backend returns `{ status: "out_of_scope", cooldown_seconds: 10 }`.
   - The widget activates an accessible, full-screen visual overlay that randomly spawns warning badges across the viewport with randomized rotations, scales, shake/pulse animations, and locked input.
   - Automatically cleans up all timers and restores normal chat functionality after exactly 10 seconds.
