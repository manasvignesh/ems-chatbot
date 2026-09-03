# AI Guardrails & Scope Security Policy

EMS Assistant enforces strict security guardrails to ensure reliable, student-focused event assistance and protect infrastructure from abuse, prompt injection, and hallucination.

---

## 1. Domain Scope Matrix

| Category | Status | Treatment |
| :--- | :--- | :--- |
| **EMS Events & Workshops** | Allowed | Answer grounded in retrieved EMS chunks |
| **Schedules, Venues & Dates** | Allowed | Exact factual retrieval from EMS database |
| **Registration & Eligibility** | Allowed | Exact factual retrieval from EMS database |
| **Rules & Prerequisites** | Allowed | Exact factual retrieval from EMS database |
| **Event Preparation Guidance** | Allowed | EMS context combined with safe general reasoning |
| **Technical Event Concepts** (e.g. "What is IoT?") | Allowed | Concise explanation in context of the workshop |
| **Sports / Entertainment / Movies** | Blocked | `OUT_OF_SCOPE` -> 10s Error Spam Cooldown |
| **Unrelated Homework / Assignments** | Blocked | `OUT_OF_SCOPE` -> 10s Error Spam Cooldown |
| **Financial / Stock Advice** | Blocked | `OUT_OF_SCOPE` -> 10s Error Spam Cooldown |
| **Malware / Exploits / Hacking** | Blocked | `OUT_OF_SCOPE` -> 10s Error Spam Cooldown |
| **System Prompt / Secret Sniffing** | Blocked | `OUT_OF_SCOPE` -> 10s Error Spam Cooldown |

---

## 2. Prompt Injection Defense

1. **Passive Document Isolation**:
   - Retrieved PDF and text chunks are stripped of pseudo-instruction XML/HTML tags (e.g. `<system>`, `<rules>`) before insertion into the prompt.
   - The LLM is explicitly instructed that retrieved context is *passive data* and can never override system rules.

2. **Credential Sniffing Blocklist**:
   - Overt attempts to request API keys, Supabase credentials, tokens, or administrative roles are blocked before reaching generation.

3. **Grounded Factuality Constraint**:
   - The system prompt forbids guessing or interpolating dates, timings, venues, deadlines, or rules. If missing from the RAG store, the assistant must explicitly state that the information is unavailable.

---

## 3. 10-Second Error Spam Effect & Cooldown

When an out-of-scope question is submitted:
1. The backend immediately responds with `{ "status": "out_of_scope", "cooldown_seconds": 10 }`.
2. The widget mounts a full-screen overlay to `document.body` with `pointer-events: none` and random shaking/pulsing warning badges across the viewport.
3. Chat input is disabled with a 10-second countdown timer.
4. Screen readers receive a single polite announcement: *"This question is outside the EMS Assistant scope. Chat is temporarily unavailable for 10 seconds."*
5. Once the 10-second countdown reaches 0, all intervals and overlay nodes are completely removed without page reload.
