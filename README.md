# 🇮🇳 Policy-Navigator — Citizen Advocate AI

> **Zynd Aickathon 2026** — Building Agent Advocates that simplify Indian government policies, verify eligibility, and deliver trust-backed recommendations via the Zynd Protocol.

---

## 🏗️ Project Structure

```
policy-Navigator/
│
├── data/
│   ├── __init__.py
│   └── dummy_data.py          # 3 scheme datasets: Scholarship, Farming, Startup
│
├── scripts/
│   ├── __init__.py
│   └── query_agent.py         # RAG-based AI agent with Citizen Advocate system prompt
│
├── vector_db/                 # Auto-created by ingest.py (ChromaDB)
│
├── ingest.py                  # One-time data ingestion → ChromaDB
├── zynd_node.py               # Zynd Protocol registration + DID assignment
│
├── .env                       # API keys (NEVER commit this)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone & Setup

```bash
git clone <your-repo-url>
cd policy-Navigator
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env` and fill in your keys:

```bash
# .env
GOOGLE_API_KEY=your_google_gemini_api_key
ZYND_API_KEY=your_zynd_api_key
```

Get your **Google API Key** → [makersuite.google.com](https://makersuite.google.com/app/apikey)

### 3. Ingest Scheme Data into ChromaDB

```bash
python ingest.py
```

This reads `data/dummy_data.py`, generates embeddings via **Gemini**, and persists them to `./vector_db`.

### 4. Chat with the Citizen Advocate

```bash
python scripts/query_agent.py
```

Ask in **Hindi, English, or Hinglish**:
```
You: Main ek minority student hoon Class 9 mein. Scholarship milegi?
Neeti: 📋 Eligibility ke baare mein batata hoon...
```

### 5. Register on Zynd Protocol

```bash
python zynd_node.py
```

This generates a **Decentralized Identity (DID)**, registers the agent on the Zynd network, and saves `agent_identity.json`.

---

## 🤖 Agent Behavior

When you ask a question, **Neeti (Citizen Advocate)** will:

| Step | Action |
|------|--------|
| 📋 **Summarize** | Explain the policy in simple Hinglish |
| ✅ **Eligibility** | Clearly state who qualifies and who doesn't |
| ❓ **Ask questions** | Request missing info (income/age/category/land) |
| 📝 **Next Steps** | Provide numbered application instructions + portal URL |
| 🔐 **Trust signal** | End with: *Verified by Neeti via Zynd Protocol* |

---

## 🗂️ Supported Schemes

| ID | Scheme | Category |
|----|--------|----------|
| `scheme_001` | NSP Pre-Matric Scholarship | Scholarship |
| `scheme_002` | PM-KISAN | Farming / Agriculture |
| `scheme_003` | Startup India Seed Fund (SISFS) | Startup |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| AI Model | `gemini-1.5-flash` (Google Gemini) |
| Embeddings | `models/embedding-001` (Google) |
| RAG Framework | LangChain |
| Vector Store | ChromaDB (`./vector_db`) |
| Agent Registry | Zynd Protocol SDK |
| Language | Python 3.10+ |

---

## 🌐 Zynd Protocol Integration

`zynd_node.py` performs:
1. **DID Generation** — SHA-256 fingerprint → `did:zynd:<name>:<hash>`
2. **Agent Card Creation** — name, capabilities, trust level, endpoint
3. **Network Registration** — via `zynd_sdk.register_agent()`
4. **Identity Persistence** — saves `agent_identity.json`

> If `zynd-sdk` is not installed, the node runs in **Simulation Mode** and generates a local DID for demonstration.

---

## 📄 License

MIT — Built for Zynd Aickathon 2026. Jai Hind! 🇮🇳
