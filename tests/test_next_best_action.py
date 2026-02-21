"""
tests/test_next_best_action.py
Unit tests for logic.next_best_action.handle_policy_request()

Uses a mock FAISS-like object so no API keys or index files are required.
Run with:  python -m pytest tests/test_next_best_action.py -v
"""

import pytest
from unittest.mock import MagicMock
from langchain_core.documents import Document
from logic.next_best_action import handle_policy_request


# ─────────────────────────────────────────────────────────────────────────────
# Mock FAISS helper
# ─────────────────────────────────────────────────────────────────────────────

def make_mock_faiss(docs: list[Document]):
    """
    Return a mock object that mimics FAISS.similarity_search() returning *docs*.
    """
    mock_db = MagicMock()
    mock_db.similarity_search.return_value = docs
    return mock_db


def make_doc(scheme_id: str, title: str, category: str,
             max_income_inr: float = float("inf"),
             min_age: int = 0, max_age: int = 999) -> Document:
    return Document(
        page_content=f"Scheme: {title}",
        metadata={
            "scheme_id": scheme_id,
            "title": title,
            "category": category,
            "max_income_inr": max_income_inr,
            "min_age": min_age,
            "max_age": max_age,
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 — Direct eligibility success (target scheme check passes)
# ─────────────────────────────────────────────────────────────────────────────

def test_success_path_no_redirect_needed():
    """
    User IS eligible for the target scheme → status='success',
    FAISS should never be queried.
    """
    user = {"age": 12, "income": 80_000, "community": "Muslim"}
    target = "scheme_001"

    mock_db = make_mock_faiss([])          # no docs needed — success exits early
    result = handle_policy_request(user, target, mock_db)

    assert result["status"] == "success"
    assert result["alternative"] is None
    mock_db.similarity_search.assert_not_called()


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 — Income rejection → redirect to eligible alternative
# ─────────────────────────────────────────────────────────────────────────────

def test_redirect_income_too_high_for_target():
    """
    User income ₹3L exceeds scheme_001 cap (₹1L).
    FAISS returns scheme_010 (PMS-SC, cap ₹2.5L) which the user still fails,
    then scheme_007 (PMKVY, no income cap + age 22 fits) → redirect.
    """
    user = {"age": 22, "income": 300_000, "community": "SC"}
    target = "scheme_001"   # cap ₹1L

    # scheme_010 has cap ₹2.5L — still fails for ₹3L income
    doc_010 = make_doc("scheme_010", "PMS-SC Scholarship", "Scholarship", max_income_inr=250_000, min_age=16)
    # scheme_007 has no income cap — user age 22 fits (18–45)
    doc_007 = make_doc("scheme_007", "PMKVY 4.0", "Skill Development", max_income_inr=float("inf"), min_age=18, max_age=45)

    mock_db = make_mock_faiss([doc_010, doc_007])
    result = handle_policy_request(user, target, mock_db)

    assert result["status"] == "redirect"
    assert result["alternative"] is not None
    assert result["alternative"]["scheme_id"] == "scheme_007"
    assert "scheme_007" in result["message"] or "PMKVY" in result["message"]
    mock_db.similarity_search.assert_called_once()


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 — No suitable alternative exists
# ─────────────────────────────────────────────────────────────────────────────

def test_no_alternative_found():
    """
    FAISS returns schemes that also fail eligibility checks → status='failed'.
    """
    user = {"age": 10, "income": 50_000, "community": "Muslim"}
    target = "scheme_002"   # must_be_farmer

    # scheme_008 requires age >= 60 (user is 10) — fails
    doc_008 = make_doc("scheme_008", "IGNOAPS Pension", "Pension", min_age=60, max_age=999)
    # scheme_006 requires female + rural (profile has neither) — fails
    doc_006 = make_doc("scheme_006", "Mahila Shakti Kendra", "Women", min_age=18)

    mock_db = make_mock_faiss([doc_008, doc_006])
    result = handle_policy_request(user, target, mock_db)

    assert result["status"] == "failed"
    assert result["alternative"] is None
    assert result["reason"] is not None


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 — Target scheme skipped in alternatives list
# ─────────────────────────────────────────────────────────────────────────────

def test_target_scheme_skipped_in_candidates():
    """
    If FAISS returns the same scheme as the target (possible with cosine sim),
    it must be skipped and not returned as an 'alternative'.
    """
    user = {"age": 22, "income": 300_000, "community": "SC"}
    target = "scheme_001"

    # First candidate is the rejected scheme itself — must be skipped
    doc_001 = make_doc("scheme_001", "NSP Pre-Matric", "Scholarship", max_income_inr=100_000, max_age=17)
    # Second is a valid alternative
    doc_007 = make_doc("scheme_007", "PMKVY 4.0", "Skill", max_income_inr=float("inf"), min_age=18, max_age=45)

    mock_db = make_mock_faiss([doc_001, doc_007])
    result = handle_policy_request(user, target, mock_db)

    assert result["status"] == "redirect"
    assert result["alternative"]["scheme_id"] != "scheme_001"
    assert result["alternative"]["scheme_id"] == "scheme_007"


# ─────────────────────────────────────────────────────────────────────────────
# Test 5 — FAISS query uses the right default query text
# ─────────────────────────────────────────────────────────────────────────────

def test_faiss_called_with_query_text():
    """
    When rejection occurs, FAISS similarity_search must be called with the
    expected query text (default or custom).
    """
    user = {"age": 10, "is_farmer": False}   # fails scheme_002
    target = "scheme_002"
    custom_query = "financial help scheme"

    mock_db = make_mock_faiss([])
    handle_policy_request(user, target, mock_db, query_text=custom_query)

    mock_db.similarity_search.assert_called_once_with(custom_query, k=8)


# ─────────────────────────────────────────────────────────────────────────────
# Test 6 — FAISS error is handled gracefully
# ─────────────────────────────────────────────────────────────────────────────

def test_faiss_error_returns_failed():
    """If FAISS raises an exception, the NBA layer returns status='failed'."""
    user = {"age": 10, "is_farmer": False}
    target = "scheme_002"

    mock_db = MagicMock()
    mock_db.similarity_search.side_effect = RuntimeError("Index file missing")

    result = handle_policy_request(user, target, mock_db)
    assert result["status"] == "failed"
    assert "FAISS" in result["message"] or "error" in result["message"].lower()
