# JOLLY-LLB Test Suite Reference

This directory contains the verification layers for JOLLY-LLB, ensuring that the automation, rules, and redirects all function reliably before deployment.

## 📁 Test Modules

### 1. `test_agent.py` — End-to-End Automation
This is the flagship test suite for the Form Filler agent. It runs in two distinct phases:

-   **Phase 1 (Dummy Portal)**: Fully automated. It launches the internal FastAPI server, navigates to the professional dummy portal, and verifies that the agent can successfully fill and submit a form with 100% reliability.
-   **Phase 2 (Real Portal)**: Semi-automated verification on the real **PM-KISAN** website. It handles browser navigation, Aadhaar entry, and OTP triggering, pausing for the human to enter the OTP before completing the registration form.

**Usage**:
```bash
# Run both phases
python tests/test_agent.py

# Run only dummy portal verification
python tests/test_agent.py --phase1
```

---

### 2. `test_eligibility.py` — Deterministic Rules (Unit Tests)
This module verifies the **Rule Engine** in `logic/eligibility_engine.py`. It contains 30+ test cases that validate strict eligibility criteria (Age, Income, Community, Land Holding) for various government schemes.
-   Uses `pytest` for fast, offline verification.
-   Ensures 0% LLM hallucination in eligibility checks.

**Usage**:
```bash
python -m pytest tests/test_eligibility.py -v
```

---

### 3. `test_next_best_action.py` — Redirection Logic
Tests the redirection intelligence in `logic/next_best_action.py`.
-   **Mock Integration**: Uses mock FAISS objects to simulate "searching for alternatives" without needing live API keys.
-   **Scenarios**: Verifies that if a user is rejected from "Scheme A", the system correctly identifies and redirects them to the most relevant "Scheme B" that they *actually* qualify for.

**Usage**:
```bash
python -m pytest tests/test_next_best_action.py -v
```

---

## 🛠️ Running the full suite
For a complete system health check:
```bash
python scripts/test_pipeline.py && python -m pytest tests/test_eligibility.py tests/test_next_best_action.py
```

> [!NOTE]
> Ensure the backend server (`uvicorn api.server:app`) is NOT already running on port 8000 when starting `test_agent.py`, as the test script manages its own server lifecycle.
