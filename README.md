# The Equinox 2.0 Assistant — Standalone AI Chatbot & Embeddable Widget

**The Equinox 2.0 Assistant** is a high-precision, production-quality AI Event Assistant built specifically for **The Equinox 2.0** (the 2-day flagship E-Summit hosted by the **Centre for Innovation & Entrepreneurship (CIE)** at **MLR Institute of Technology, Hyderabad**).

The chatbot runs as an autonomous Python FastAPI service with an embeddable React + TypeScript Shadow DOM widget, featuring sub-event precision retrieval, comprehensive precomputed FAQs, typo tolerance, authoritative timezone grounding, and prompt injection defense.

---

## 🌟 Key Features

1. **Authoritative Equinox 2.0 Knowledge Base**:
   - Strictly derived from official brochure and prospectus documents.
   - Deep structured knowledge for all **10 flagship sub-events**:
     1. **Spotlight** (Industry expert keynote talks on tech & startups)
     2. **Crossroads** (Business case-study competition)
     3. **Startup Expo** (Startups showcasing products & solutions)
     4. **Brand Battles** (Competitive brand debate)
     5. **IPL Auction** (Simulated cricket auction & team budget strategy)
     6. **Hustle Mania** (Live product selling & negotiation challenge)
     7. **Internship Drive** (Direct hiring connections with startups & companies)
     8. **Startup Poly** (Monopoly-inspired business simulation game)
     9. **E-Cell Meet** (Cross-campus E-Cell collaboration & networking)
     10. **Pitch Deck** (Startup pitching to investors & industry mentors)
   - Sponsorship packages (Associate, Premium, Exclusive, Title) and past sponsor citations.
   - Official contact details and venue information.

2. **Minimizing Gemini (Precomputed FAQ & Small-Talk Layer)**:
   - High-confidence deterministic FAQ matcher with 60+ categorized question clusters and extensive variants.
   - Standard queries ("What is Equinox?", "When is Equinox?", "Where is it?", "What events are there?", "Tell me about IPL Auction", "Who can I contact?") respond in **$< 1$ ms with 0 vector lookups and 0 Gemini calls**.
   - >90% Gemini avoidance rate on standard Equinox queries.

3. **Domain Typo & Alias Tolerance**:
   - RapidFuzz token-sort similarity & domain alias normalization (`"spotlite"` ➔ `"spotlight"`, `"ipl action"` ➔ `"ipl auction"`, `"startup polly"` ➔ `"startup poly"`).

4. **10-Second Randomized Error Spam Effect**:
   - Triggers a playful 10-second randomized spam window effect for clearly out-of-scope queries (e.g. real IPL match scores, homework requests) with a cooldown timer.

5. **Authoritative Time Engine**:
   - Timezone-aware datetime context (`Asia/Kolkata`) with strict adherence to official 30–31 October summit dates without year hallucination.

---

## 🚀 Quick Start

### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Widget Build
```bash
cd widget
npm install
npm run build
```

### 3. Running Acceptance Tests
```bash
python -m pytest backend/tests -v
```

---

## 🌐 Demo Portal & Endpoints

- **Portal Home**: `http://localhost:8000/demo/index.html`
- **Sub-Event Detail Page**: `http://localhost:8000/demo/event.html?id=startup-poly`
- **Swagger Documentation**: `http://localhost:8000/docs`
