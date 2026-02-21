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

- **`data/dummy_data.py`** — 3 richly structured schemes (NSP Scholarship, PM-KISAN, Startup India SISFS), each with eligibility rules, benefits, documents required, and portal URLs
- **`ingest.py`** — Embeds all schemes via Google Gemini, stores to FAISS index (`faiss_index/`) — **tested and working**
- **`scripts/query_agent.py`** — Full RAG pipeline: FAISS retrieval → CITIZEN_ADVOCATE_PROMPT → Groq LLM → response with sources — **tested and working**
- **`zynd_node.py`** — Generates deterministic DID, registers agent (Simulation Mode if SDK absent), saves `agent_identity.json`
- **`test_pipeline.py`** — Step-by-step test validating embeddings → retrieval → LLM (all 3 passed ✅)
- **`.env`** — `GOOGLE_API_KEY` + `GROQ_API_KEY` + `ZYND_API_KEY` configured

### ❌ Not Yet Built

- **Rule Engine** — The core innovation: deterministic Python boolean logic to verify eligibility (`if user.age >= policy.min_age`) *without* relying on the LLM — currently LLM decides eligibility (hallucination risk)
- **User Profile Extractor** — Structured `user_profile = {"age": 22, "income": 150000}` JSON extracted from conversation (needed for rule engine)
- **Web Scraper** — Real scheme data from MyScheme.gov.in (currently only 3 hardcoded schemes)
- **More Schemes** — Need 20–50+ schemes to be useful
- **Frontend / UI** — No chat interface yet (CLI only); Streamlit or a simple HTML page needed for demo
- **FastAPI endpoint** — Required for Zynd network to route external agent calls to this agent (not needed for local demo)

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
