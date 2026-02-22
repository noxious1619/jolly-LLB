# 🇮🇳 JOLLY-LLB: Citizen Advocate AI — Technical Pitch

**Zynd Aickathon 2026** — A Trust-First, Deterministic AI Agent for Indian Government Policy Navigation

---

## Executive Summary

**JOLLY-LLB** is a production-ready Citizen Advocate AI that simplifies access to Indian government schemes. Unlike traditional chatbots that rely solely on LLM reasoning (prone to hallucinations), JOLLY-LLB combines:
- **Deterministic Logic Gates** (hardcoded Python rules) for eligibility verification
- **RAG-Powered Retrieval** (FAISS + Gemini embeddings) for policy discovery
- **Playwright-based Automation** for zero-touch form filling
- **Zynd Protocol Integration** for trust-first agent verification

**Key Innovation:** Decoupling conversational flow (Track 1) from deterministic decision logic (Track 2) eliminates LLM hallucinations while maintaining a natural user experience.

---

## System Architecture

```
User Query (Streamlit Dashboard)
    ↓
┌─────────────────────────────────────────┐
│  TRACK 1: Conversational & Extraction   │
├─────────────────────────────────────────┤
│ 1. Intent Classification (Groq LLM)     │
│    → Is this a policy question?         │
│ 2. User Profile Extraction (Groq LLM)   │
│    → Parse age, income, occupation...   │
│ 3. Memory Management                    │
│    → Accumulate data across turns       │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  TRACK 2: Logic & Eligibility Gate      │
├─────────────────────────────────────────┤
│ 1. Semantic Search (FAISS)              │
│    → Retrieve matching schemes          │
│ 2. Deterministic Eligibility Check      │
│    → Python rules (no LLM involvement)  │
│ 3. Next Best Action (NBA)               │
│    → Redirect if ineligible             │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Response & Action Panel                │
├─────────────────────────────────────────┤
│ • Eligibility verdict + explanation     │
│ • "Auto-Fill" button → Playwright agent │
│ • PDF checklist generation              │
└─────────────────────────────────────────┘
```

---

## Test Suite Overview

The test structure validates each layer independently, ensuring robustness:

### **1. Track-2: Deterministic Logic Tests**
**Purpose:** Verify eligibility rules work without any LLM or API calls.

#### `verify_track2.py` (22 unit tests)
- **Function:** Lightweight standalone verification of the eligibility engine
- **Coverage:** Tests all three major schemes with edge cases
- **Why it matters:** Proves the deterministic gates are bulletproof
- **Test Examples:**
  - ✅ NSP Scholarship: Eligible minority student (age 12, income ₹80k)
  - ❌ NSP Scholarship: Income too high (₹200k exceeds ₹1L cap)
  - ✅ PM-KISAN: Eligible farmer (age 40)
  - ❌ PM-KISAN: Excluded occupation (income tax payer)
  - ✅ Startup India: Eligible DPIIT startup (1.5 years old, <₹1M prior funding)
  - ❌ Startup India: Startup too old (3 years exceeds 2-year limit)
- **Key Assertion:** No external dependencies — pure Python logic

#### `tests/test_eligibility.py` (Full pytest suite)
- **Function:** Comprehensive pytest-based unit tests for `verify_eligibility()`
- **Coverage:** 50+ test cases for schemes 001, 002, 003
- **Key Tests:**
  - Income boundary checks (at/above/below thresholds)
  - Age range validation (min/max constraints)
  - Community/occupation filtering
  - Attendance percentage thresholds
  - Complex logic (exclusive/inclusive rules)
- **Defensive Testing:** Case-insensitive community names, missing fields, invalid schemes

#### `tests/test_next_best_action.py` (NBA engine tests)
- **Function:** Tests the "redirect if ineligible" logic
- **Coverage:** Verifies scheme-to-scheme fallback chains
- **Key Scenario:**
  - User ineligible for NSP (scholarship) → Recommend PM-KISAN (farming)
  - User ineligible for all schemes → Suggest documentation improvements
- **Why it matters:** Ensures every rejection is paired with an alternative path

---

### **2. Track-1: Conversational & Extraction Tests**

#### `test_integration.py` (9+ integration tests)
- **Function:** Full pipeline test with mocked FAISS and LLM
- **Coverage:** Intent classification → extraction → eligibility → response
- **Key Scenarios:**
  1. **Casual Intent**: User says "Hi" → Falls back to conversation memory (no policy search)
  2. **Policy Search**: User says "Am I eligible for scholarships?" → Triggers FAISS retrieval
  3. **Profile Building**: Multi-turn extraction: "I'm 14, earning ₹80k, Muslim" → Accumulate fields
  4. **Eligibility Gate**: Call Track-2 logic on extracted profile
  5. **Alternative Schemes**: If ineligible, suggest alternatives with NBA
  6. **Error Handling**: Missing FAISS index, API timeouts, invalid schemes
- **Mock Fixtures:** 
  - Mock FAISS returns predictable documents
  - Mock Groq LLM with hardcoded responses
  - Mock memory to track conversation history
- **Assertions:** Response contains correct scheme_id, eligibility status, and follow-up action

#### `test_flow.py` (Conversational flow validation)
- **Function:** End-to-end manual test of the FlowController
- **Coverage:** 4-turn conversation in Hindi/English mix
- **Test Dialogue:**
  ```
  User: "Hi"                              → Casual greeting
  User: "Main minority student hoon"      → Intent: policy_search
  User: "14 saal ka hoon"                 → Extract age: 14
  User: "Meri income 80000 hai"           → Extract income: 80,000
  → System checks eligibility for NSP
  → Returns: "✅ You are eligible!"
  ```
- **Why it matters:** Validates the multi-turn memory accumulation in real conversational context

#### `test_router.py` (Intent classification)
- **Function:** Tests the semantic router (casual vs. policy intent)
- **Input:** A user message (e.g., "Meri income 80000 hai")
- **Output:** Intent label (e.g., "provide_income")
- **Why it matters:** Ensures the system correctly classifies user intent before routing

---

### **3. Retrieval & Embedding Tests**

#### `test_pipeline.py` (Full RAG pipeline)
- **Function:** Tests the end-to-end retrieval pipeline
- **Steps:**
  1. Embed user query with Google Gemini embedding model
  2. Retrieve similar policies from FAISS index
  3. Pass retrieved documents to Groq LLM
  4. LLM synthesizes a user-friendly answer
- **Key Assertion:** Answer mentions correct scheme names and eligibility criteria
- **Dependencies:** Requires `.env` keys (GOOGLE_API_KEY, GROQ_API_KEY)

#### `test_extractor.py` (Profile extraction)
- **Function:** Tests structured extraction of user demographics
- **Coverage:**
  - Extract `age`, `income`, `community`, `occupation` from unstructured text
  - Validate extracted types (int, float, string)
  - Handle missing fields gracefully
  - Pydantic schema validation

---

### **4. Additional Tests**

#### `test_memory.py`
- **Function:** Validates conversation memory management
- **Coverage:** Merge profiles across turns, maintain history, clear on new session

#### `test_rule_engine.py`
- **Function:** Tests individual rule evaluation functions
- **Coverage:** Age checks, income thresholds, document requirements

#### `test_agent.py` (agents/ folder)
- **Function:** Tests the Playwright form-filling agent
- **Coverage:** Browser launch, field detection, auto-fill, submission

---

## Complete Application Flow

### **Step 1: User Submits Query (Streamlit Dashboard)**
```python
User Input: "Am I eligible for PM-KISAN? I'm a farmer, 35 years old."
Session State: profile = {age: 35, is_farmer: True, ...}
```
- User enters demographics via sidebar form expanders
- User types question in chat input
- Streamlit sends to backend via `ask_agent_with_eligibility()`

### **Step 2: Intent Classification (Track 1)**
**File:** `app/routers.py:classify_intent()`
```
Message: "Am I eligible for PM-KISAN?"
↓
Groq LLM Classification
↓
Intent: "policy_search"
Confidence: 0.95
```
- If intent = "casual" → Route to ConversationMemory (no policy search)
- If intent = "policy_search" → Continue to extraction

### **Step 3: User Profile Extraction (Track 1)**
**File:** `app/extractor.py:extract_user_profile()`
```
Message: "I'm 35, a farmer, with family income ₹5 lakh"
↓
Groq LLM + Pydantic parser
↓
Extracted: {
  "age": 35,
  "is_farmer": True,
  "income": 500_000,
  "occupation": "farmer"
}
```
- Parse structured fields from conversational text
- Handle typos, regional language, abbreviated numbers
- Return Pydantic `UserProfile` object

### **Step 4: Profile Accumulation (Track 1)**
**File:** `app/memory.py:ConversationMemory.merge_profile()`
```
Session Turn 1: Age extracted → memory = {age: 35}
Session Turn 2: Income extracted → memory = {age: 35, income: 500_000}
Session Turn 3: Community extracted → memory = {age: 35, income: 500_000, community: "OBC"}
```
- Maintain per-session memory across multiple turns
- Don't overwrite existing values (preserve earlier answers)
- Signal when missing critical fields

### **Step 5: Check Missing Fields (Track 1)**
**File:** `app/extractor.py:check_missing_fields()`
```python
Required for scheme_002 (PM-KISAN):
  • age ✅ (provided: 35)
  • is_farmer ✅ (provided: True)
  • occupation ✅ (provided: farmer)
  • income ❌ (missing!)

Action: Pause and ask "What is your annual family income?"
```
- Identify which required fields are still missing
- Prompt user for critical information before gating

### **Step 6: Semantic Search & Scheme Matching (Track 2)**
**File:** `scripts/query_agent.py:load_vector_db()` + FAISS
```
Query: "PM-KISAN eligibility"
↓
1. Embed with Gemini embeddings (768-dim vector)
2. Search FAISS index for similar scheme descriptions
3. Retrieve top-3 matching documents
↓
Results: [
  {scheme_id: "scheme_002", title: "PM-KISAN", score: 0.92},
  {scheme_id: "scheme_001", title: "NSP Scholarship", score: 0.45},
]
```
- FAISS index built by `ingest.py` from policy documents
- Hybrid ranking: semantic relevance + manual scheme boost

### **Step 7: Deterministic Eligibility Gate (Track 2)**
**File:** `logic/eligibility_engine.py:verify_eligibility()`
```python
User Profile: {age: 35, is_farmer: True, occupation: "farmer", ...}
Scheme: "scheme_002" (PM-KISAN)
↓
Check Rules:
  • Is age >= 18? YES ✅
  • Is is_farmer = True? YES ✅
  • Is occupation in excluded list? NO ✅
  • Family income limit? (no limit for PM-KISAN) ✅
↓
Result: (True, "Eligible")
```
- Pure Python logic — no LLM involvement (prevents hallucinations)
- Returns `(bool, reason_string)` tuple
- Handles all eligibility constraints from `POLICY_DB`

### **Step 8: Next Best Action (NBA) - Track 2**
**File:** `logic/next_best_action.py:handle_policy_request()`

#### Scenario A: User is Eligible
```
Status: "success"
Message: "✅ You are eligible for PM-KISAN!"
Action: Show "Auto-Fill" button
```
- Grant eligibility verdict
- Enable form-filling automation

#### Scenario B: User is Ineligible (but alternatives exist)
```
User: Ineligible for scheme_001 (NSP - income too high: ₹500k > ₹1L)
↓
NBA Engine searches for alternatives
↓
Alternative found: scheme_002 (PM-KISAN)
  - User is a farmer (matches requirement)
  - No income limit (user's ₹500k is fine)
  - User age 35 is within range
↓
Status: "redirect"
Message: "❌ Too much income for NSP. But ✅ Try PM-KISAN instead!"
Action: Offer auto-fill for scheme_002
```
- Search through policy database for schemes where user IS eligible
- Rank alternatives by relevance
- Suggest best match with personalized reason

#### Scenario C: User is Ineligible (no alternatives)
```
Status: "failed"
Message: "❌ You don't qualify. Try improving: [list missing docs/criteria]"
Action: Show PDF checklist for future eligibility
```
- Provide actionable next steps (e.g., "Wait 1 year for startup to qualify")

### **Step 9: RAG Synthesis (Track 1)**
**File:** `scripts/query_agent.py:ask_agent()`
```
Context: 
  • Retrieved docs (policy descriptions)
  • User profile (extracted demographics)
  • Eligibility verdict from Track-2

Prompt: "Given that the user is eligible for PM-KISAN, explain:
         1. What is PM-KISAN?
         2. How much money will they get?
         3. How long is the benefit period?"

↓
Groq Llama 3.3 LLM
↓
Answer: "PM-KISAN is a direct income support scheme...
         You'll receive ₹6,000 per year in 3 installments...
         Benefit runs indefinitely for eligible farmers..."
```
- Use retrieved documents as factual grounding
- LLM explains (not decides) eligibility
- Combine with Track-2 verdict for final response

### **Step 10: Response + Action Panel (Frontend)**
**File:** `app.py` (Streamlit)
```
┌─────────────────────────────────────┐
│ JOLLY-LLB - Citizen Advocate        │
├─────────────────────────────────────┤
│ Assistant:                          │
│ ✅ Status: SUCCESS                  │
│ PM-KISAN (Pradhan Mantri Kisan      │
│ Samman Nidhi) is perfect for you!   │
│                                     │
│ You'll receive ₹6,000 per year...   │
│                                     │
├─────────────────────────────────────┤
│ [🚀 Start Auto-Fill]  [📄 PDF Doc]  │
└─────────────────────────────────────┘
```

### **Step 11: Form Automation (Optional)**
**File:** `api/server.py:start_form()` + `agents/form_filler.py`

When user clicks "Auto-Fill":

1. **Browser Launch** (Playwright)
   ```
   POST /start-form
   ↓
   Launch Chromium (visible window)
   Navigate to: http://127.0.0.1:8001/static/dummy_portal.html
   Pause until user logs in
   ```

2. **User Manual Login** (Security)
   ```
   User manually enters credentials in standing browser window
   (Agent waits, doesn't steal passwords)
   User clicks "I'm Logged In - Fill Form!"
   ```

3. **Automated Filling** (Playwright)
   ```
   POST /resume-form
   ↓
   Playwright reads CSS selectors from SCHEME_FIELD_MAP
   ↓
   For each field: {
     "full_name": "Sagar Bhai"
     "age": 35
     "income": 500000
     "state": "Uttar Pradesh"
     ...
   }
   
   Simulate human typing (0.5s delay per field)
   Click Submit button
   ```

4. **Completion**
   ```
   ✅ Form submitted successfully
   Show confirmation + next steps
   ```

---

## Key Testing Patterns

### Pattern 1: Unit Tests (No Dependencies)
```python
# verify_track2.py, tests/test_eligibility.py
from logic.eligibility_engine import verify_eligibility

ok, reason = verify_eligibility({
    "age": 12,
    "income": 80_000,
    "community": "Muslim"
}, "scheme_001")

assert ok is True
assert reason == "Eligible"
```
**Why:** Fast, reproducible, no API keys needed

---

### Pattern 2: Integration Tests (With Mocks)
```python
# test_integration.py
from unittest.mock import MagicMock, patch

mock_faiss = MagicMock()
mock_faiss.similarity_search.return_value = [
    Document(metadata={"scheme_id": "scheme_001", ...})
]

with patch('app.flow_controller.load_vector_db', return_value=mock_faiss):
    flow = FlowController()
    result = await flow.handle_message("Am I eligible for scholarships?")
    
    assert "scheme_001" in result["scheme_id"]
    assert result["nba_status"] in ("success", "redirect", "failed")
```
**Why:** Tests full flow without external API calls

---

### Pattern 3: End-to-End Tests (Real APIs)
```python
# test_pipeline.py
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS

db = FAISS.load_local("./faiss_index", embeddings)
results = db.similarity_search(query)
llm_answer = ChatGroq().invoke(results)
```
**Why:** Validates production behavior (requires API keys)

---

## Verification Checklist

Run the full test suite:
```bash
python verify_track2.py          # 22 offline tests
python -m pytest test_integration.py -v  # 9+ integration tests
python -m pytest tests/test_eligibility.py tests/test_next_best_action.py -v  # 50+ scheme tests
```

**Expected Output:**
```
[✅ PASS] 001-eligible-basic
[✅ PASS] 001-income-too-high
[✅ PASS] 002-eligible-farmer
[✅ PASS] 002-not-a-farmer
...
============================================================
   ALL TESTS PASSED
============================================================
```

---

## Why This Architecture Matters

| Problem | JOLLY-LLB Solution |
|---------|-------------------|
| LLM hallucinations on eligibility | Deterministic Python gate (no LLM involved) |
| Slow multi-turn queries | Conversation memory accumulates info |
| No follow-up actions when rejected | NBA engine suggests alternatives |
| Manual form filling burden | Playwright automation (0-click after approval) |
| Can't test without API keys | Offline unit tests validate core logic |
| Trust concerns (Zynd requirement) | Protocol signing + transparent decision logging |

---

## Deployment Readiness

- ✅ **Offline Tests:** 22 + 50+ = 72 deterministic unit tests (no API calls)
- ✅ **Integration Tests:** 9+ mocked pipeline tests
- ✅ **Error Handling:** Graceful fallbacks for API failures
- ✅ **Windows Compatibility:** ProactorEventLoop for Playwright subprocess
- ✅ **Security:** No password storage (user enters credentials)
- ✅ **Scalability:** Stateless FastAPI backend + per-session Streamlit memory

---

## Next Steps (Post-Aickathon)

1. **Production Policies:** Replace dummy schemes with real govt. policies (MYSCHEME.GOV.IN)
2. **Multi-Language NLU:** Handle Hindi, Tamil, Telugu, Bengali queries
3. **Document OCR:** Auto-extract eligibility criteria from PDF policy docs
4. **Zynd Chain Integration:** Immutable audit log of eligibility decisions
5. **Analytics Dashboard:** Track user demographics, scheme popularity, NBA success rate

---

## Team Attribution

- **Track 1 (Conversational & Extraction):** Garv → Intent classification, profile extraction, memory management
- **Track 2 (Logic & Eligibility):** Core → Deterministic gates, NBA engine, eligibility verification
- **Integration & Testing:** Continuous validation across both tracks
- **Frontend & Automation:** Streamlit dashboard + Playwright form filler

---

**Built for Zynd Aickathon 2026** 🚀