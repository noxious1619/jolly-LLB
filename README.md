# 🇮🇳 JOLLY-LLB — Citizen Advocate AI

> **Zynd Aickathon 2026** — JOLLY-LLB is a high-availability Citizen Advocate AI built on the Zynd Protocol. It simplifies complex Indian government policies, provides deterministic eligibility verification, and executes automated form filling with a trust-first approach.

---

## 🎨 Professional Interface
JOLLY-LLB now features a state-of-the-art **Professional Dark Theme** dashboard built with Streamlit.
- **Architecture Stepper**: Real-time visualization of the AI's internal reasoning stages.
- **Dynamic Profile Builder**: Sidebar form to manage user demographics for precise eligibility checks.
- **Actionable AI**: Direct "Auto-Fill" integration that launches a background automation agent.

---

## 🏗️ Project Architecture

```
User Query → [ Semantic Search (FAISS) ] 
             → [ Deterministic Rule Gate ] 
             → [ RAG Synthesis (Groq Llama 3.3) ] 
             → [ Zynd Protocol Signing ] 
             → Response + Action Panel
```

### Core Features:
1.  **RAG-Powered Policy Navigator**: Semantic search across 20+ schemes using Gemini Embeddings and FAISS.
2.  **Deterministic Rule Engine**: Hardcoded Python logic guards against LLM hallucinations for eligibility checks.
3.  **Next Best Action (NBA)**: Automatically redirects users to alternative schemes if they are ineligible.
4.  **Intelligent Form Filler**: Playwright-based agent that auto-fills registration forms with 0.5s typing delay for visibility.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.12+ (Recommended)
- Chrome or Edge browser (for Playwright)

### 2. Installation & Setup
```bash
git clone <repo-url>
cd jolly-LLB
pip install -r requirements.txt
playwright install chromium
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
ZYND_API_KEY=your_zynd_api_key
```

### 4. Running the Project

#### Step A: Data Ingestion (One-time)
Embed the scheme data into the FAISS vector database:
```bash
python ingest.py
```

#### Step B: Launch Backend (FastAPI)
The backend coordinates the form-filling agent and the dummy portals:
```bash
uvicorn api.server:app --port 8000
```

#### Step C: Launch Frontend (Streamlit)
The main interactive dashboard for users:
```bash
streamlit run app.py
```

---

## 📂 Repository Structure

| File/Dir | Purpose |
|----------|---------|
| `app.py` | Professional Streamlit UI with Architecture Stepper. |
| `api/server.py` | FastAPI backend for form-filling sessions & A2A calls. |
| `agents/form_filler.py` | Playwright automation logic with slow-typing and success-hold. |
| `logic/eligibility_engine.py` | Deterministic Python rules for all supported policies. |
| `logic/next_best_action.py` | Logic for intercepting rejections and finding alternatives. |
| `scripts/query_agent.py` | Core RAG pipeline with Groq reasoning. |
| `ingest.py` | Data ingestion pipeline using Google Gemini Embeddings. |
| `templates/` | Professional dummy government portals for demo/testing. |
| `tests/` | Comprehensive test suite (Agent, Eligibility, NBA). |

---

## 🛠️ Tech Stack
- **LLM**: Groq (`llama-3.3-70b-versatile`)
- **Embeddings**: Google Gemini (`models/gemini-embedding-001`)
- **Vector Store**: FAISS
- **Automation**: Playwright
- **Identity/Trust**: Zynd Protocol
- **Web**: FastAPI & Streamlit

---

## 📄 License
MIT — Built for Zynd Aickathon 2026. Jai Hind! 🇮🇳
