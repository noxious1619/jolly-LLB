# JOLLY-LLB — Progress Tracker

## What Is This Project?

**JOLLY-LLB** (Policy-Navigator) is a Citizen Advocate AI agent that makes Indian government schemes simple and accessible. A citizen asks a question in plain English (or Hinglish), and the agent retrieves the most relevant schemes, checks eligibility, and provides step-by-step application instructions — all verified through the Zynd Protocol's trust layer.

**Hackathon:** Zynd Aickathon 2026

---

## Tech Stack

| Layer | Technology |
|---|---|
| **LLM (Chat)** | Groq — `llama-3.3-70b-versatile` (fast, no rate limits) |
| **Embeddings** | Google Gemini — `models/gemini-embedding-001` |
| **Vector DB** | FAISS (local, Python 3.14 compatible) |
| **RAG Framework** | LangChain (LCEL chains) |
| **Agent Identity** | Zynd Protocol — W3C DID (`did:zynd:<name>:<sha256>`) |
| **Language** | Python 3.14 |

---

## Architecture

```
User Question
     │
     ▼
GeminiEmbeddings          ← Google API (embed query)
     │
     ▼
FAISS Similarity Search   ← Top-3 matching schemes retrieved
     │
     ▼
CITIZEN_ADVOCATE_PROMPT   ← Context + question injected
     │
     ▼
Groq LLM (Llama 3.3 70B)  ← Generates eligibility answer + next-steps
     │
     ▼
Response to User          ← "Verified by JOLLY-LLB via Zynd Protocol"
```

---

## Current Status

### ✅ Done

- **`data/dummy_data.py`** — 3 richly structured schemes (NSP Scholarship, PM-KISAN, Startup India SISFS)
- **`ingest.py`** — Embeds all schemes via Google Gemini, stores to FAISS index — **tested and working**
- **`scripts/query_agent.py`** — Full RAG pipeline: FAISS retrieval → prompt → Groq LLM → response — **tested and working**
- **`zynd_node.py`** — Generates DID, registers agent, saves `agent_identity.json`
- **`test_pipeline.py`** — Step-by-step test: embeddings → retrieval → Groq LLM (all 3 passed ✅)
- **`app.py`** — Streamlit chat frontend with sidebar profile form, scheme detection, Apply + Fill buttons
- **`api/server.py`** — FastAPI backend with asyncio.Event pause/resume (`/start-form`, `/resume-form`, `/status`)
- **`agents/form_filler.py`** — Playwright automation: opens Chromium, pauses for login, fills fields, submits
- **`templates/dummy_portal.html`** — Realistic fake government portal (login page + application form) for demo

### ❌ Not Yet Built

- **Rule Engine** — Deterministic Python boolean eligibility check (bypasses LLM, 0% hallucination)
- **User Profile Extractor** — Auto-extract `{"age", "income", ...}` from chat conversation
- **Web Scraper** — Real scheme data from MyScheme.gov.in (currently 3 hardcoded schemes)
- **More Schemes** — Need 20–50+ schemes to be useful in production


---

## How to Run

```bash
# 1. One-time: embed schemes into FAISS
python ingest.py

# 2. Chat with JOLLY-LLB
python scripts/query_agent.py

# 3. Register on Zynd Protocol (simulation)
python zynd_node.py

# 4. Test all pipeline components
python test_pipeline.py
```

---

## Zynd Integration — Current State

The project is in **Simulation Mode**:
- ✅ DID generated: `did:zynd:policy-navigator:<sha256>`
- ✅ Agent Card created (name, capabilities, trust level)
- ❌ Not live on Zynd Network (zynd-sdk not installed, API key placeholder)
- ❌ No HTTP endpoint exposed for external agent-to-agent calls

For full Zynd integration: install `zynd-sdk`, set real `ZYND_API_KEY`, build FastAPI endpoint at `/agent`.

---

## Next Priorities

1. **Rule Engine** — highest impact, ~100 lines of Python
2. **More scheme data** — expand `dummy_data.py` or add a scraper
3. **Simple Streamlit frontend** — for demo purposes
