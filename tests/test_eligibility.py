"""
tests/test_eligibility.py
Unit tests for logic.eligibility_engine.verify_eligibility()

These tests are fully offline — no API keys, no FAISS index, no LLM.
Run with:  python -m pytest tests/test_eligibility.py -v
"""

import pytest
from logic.eligibility_engine import verify_eligibility


# ─────────────────────────────────────────────────────────────────────────────
# scheme_001 — NSP Pre-Matric Scholarship for Minorities
# ─────────────────────────────────────────────────────────────────────────────

def test_scheme001_eligible_basic():
    """Happy path: minority student within income limit."""
    user = {"age": 12, "income": 80_000, "community": "Muslim"}
    ok, reason = verify_eligibility(user, "scheme_001")
    assert ok is True
    assert reason == "Eligible"


def test_scheme001_fail_income_too_high():
    """Income exceeds ₹1 lakh cap."""
    user = {"age": 12, "income": 150_000, "community": "Muslim"}
    ok, reason = verify_eligibility(user, "scheme_001")
    assert ok is False
    assert "income" in reason.lower()


def test_scheme001_fail_age_too_high():
    """18-year-old is too old for Class 1–10 (max_age = 17)."""
    user = {"age": 18, "income": 80_000, "community": "Muslim"}
    ok, reason = verify_eligibility(user, "scheme_001")
    assert ok is False
    assert "age" in reason.lower()


def test_scheme001_fail_wrong_community():
    """Hindu community is not in the minority list."""
    user = {"age": 12, "income": 80_000, "community": "Hindu"}
    ok, reason = verify_eligibility(user, "scheme_001")
    assert ok is False
    assert "community" in reason.lower() or "Community" in reason


def test_scheme001_fail_attendance():
    """Attendance below 75% threshold."""
    user = {"age": 12, "income": 80_000, "community": "Sikh", "attendance_percent": 60}
    ok, reason = verify_eligibility(user, "scheme_001")
    assert ok is False
    assert "attendance" in reason.lower() or "Attendance" in reason


def test_scheme001_community_case_insensitive():
    """Community comparison must be case-insensitive."""
    user = {"age": 12, "income": 80_000, "community": "buddhist"}
    ok, reason = verify_eligibility(user, "scheme_001")
    assert ok is True


# ─────────────────────────────────────────────────────────────────────────────
# scheme_002 — PM-KISAN
# ─────────────────────────────────────────────────────────────────────────────

def test_scheme002_eligible_farmer():
    """Basic eligible farmer."""
    user = {"age": 40, "is_farmer": True, "occupation": "farmer"}
    ok, reason = verify_eligibility(user, "scheme_002")
    assert ok is True


def test_scheme002_fail_not_farmer():
    """Non-farmer cannot apply."""
    user = {"age": 40, "is_farmer": False}
    ok, reason = verify_eligibility(user, "scheme_002")
    assert ok is False
    assert "farmer" in reason.lower()


def test_scheme002_fail_excluded_occupation():
    """Income tax payers / professionals are excluded."""
    user = {"age": 40, "is_farmer": True, "occupation": "income_tax_payer"}
    ok, reason = verify_eligibility(user, "scheme_002")
    assert ok is False
    assert "excluded" in reason.lower() or "occupation" in reason.lower()


def test_scheme002_fail_underage():
    """Applicant must be at least 18."""
    user = {"age": 16, "is_farmer": True}
    ok, reason = verify_eligibility(user, "scheme_002")
    assert ok is False
    assert "age" in reason.lower() or "Age" in reason


# ─────────────────────────────────────────────────────────────────────────────
# scheme_003 — Startup India Seed Fund
# ─────────────────────────────────────────────────────────────────────────────

def test_scheme003_eligible_startup():
    """DPIIT-recognised startup under 2 years, no over-funding."""
    user = {
        "age": 28,
        "dpiit_recognised": True,
        "startup_age_years": 1.5,
        "prior_govt_funding_inr": 500_000,
    }
    ok, reason = verify_eligibility(user, "scheme_003")
    assert ok is True


def test_scheme003_fail_no_dpiit():
    """Startup not DPIIT-recognised."""
    user = {"age": 28, "dpiit_recognised": False, "startup_age_years": 1}
    ok, reason = verify_eligibility(user, "scheme_003")
    assert ok is False
    assert "DPIIT" in reason or "dpiit" in reason.lower()


def test_scheme003_fail_startup_too_old():
    """Startup older than 2 years."""
    user = {"age": 30, "dpiit_recognised": True, "startup_age_years": 3}
    ok, reason = verify_eligibility(user, "scheme_003")
    assert ok is False
    assert "startup" in reason.lower() or "year" in reason.lower()


def test_scheme003_fail_over_funded():
    """Prior govt funding exceeds ₹10 lakh cap."""
    user = {
        "age": 28,
        "dpiit_recognised": True,
        "startup_age_years": 1,
        "prior_govt_funding_inr": 2_000_000,
    }
    ok, reason = verify_eligibility(user, "scheme_003")
    assert ok is False
    assert "funding" in reason.lower() or "₹" in reason


# ─────────────────────────────────────────────────────────────────────────────
# scheme_007 — PMKVY (Skill Training)
# ─────────────────────────────────────────────────────────────────────────────

def test_scheme007_eligible_youth():
    """18-year-old Indian citizen within age range."""
    user = {"age": 22, "must_be_indian": True}
    ok, reason = verify_eligibility(user, "scheme_007")
    assert ok is True


def test_scheme007_fail_too_old():
    """Applicant is 46, max age is 45."""
    user = {"age": 46}
    ok, reason = verify_eligibility(user, "scheme_007")
    assert ok is False
    assert "age" in reason.lower() or "Age" in reason


def test_scheme007_fail_underage():
    """Applicant is 17, min age is 18."""
    user = {"age": 17}
    ok, reason = verify_eligibility(user, "scheme_007")
    assert ok is False


# ─────────────────────────────────────────────────────────────────────────────
# scheme_008 — IGNOAPS (Old Age Pension)
# ─────────────────────────────────────────────────────────────────────────────

def test_scheme008_eligible_senior():
    """Senior citizen above 60 from BPL household."""
    user = {"age": 65, "is_bpl": True}
    ok, reason = verify_eligibility(user, "scheme_008")
    assert ok is True


def test_scheme008_fail_too_young():
    """59-year-old is below the 60-year threshold."""
    user = {"age": 59, "is_bpl": True}
    ok, reason = verify_eligibility(user, "scheme_008")
    assert ok is False
    assert "age" in reason.lower() or "Age" in reason


def test_scheme008_fail_not_bpl():
    """Non-BPL applicant rejected."""
    user = {"age": 65, "is_bpl": False}
    ok, reason = verify_eligibility(user, "scheme_008")
    assert ok is False
    assert "bpl" in reason.lower() or "BPL" in reason


# ─────────────────────────────────────────────────────────────────────────────
# scheme_010 — Post-Matric Scholarship for SC
# ─────────────────────────────────────────────────────────────────────────────

def test_scheme010_eligible_sc_student():
    """SC student within income limit."""
    user = {"age": 19, "income": 200_000, "community": "SC"}
    ok, reason = verify_eligibility(user, "scheme_010")
    assert ok is True


def test_scheme010_fail_income_too_high():
    """Income > ₹2.5 lakh cap."""
    user = {"age": 19, "income": 300_000, "community": "Scheduled Caste"}
    ok, reason = verify_eligibility(user, "scheme_010")
    assert ok is False
    assert "income" in reason.lower()


def test_scheme010_fail_wrong_community():
    """Non-SC applicant rejected."""
    user = {"age": 19, "income": 200_000, "community": "Muslim"}
    ok, reason = verify_eligibility(user, "scheme_010")
    assert ok is False


# ─────────────────────────────────────────────────────────────────────────────
# Unknown policy
# ─────────────────────────────────────────────────────────────────────────────

def test_unknown_policy_id():
    """Graceful rejection for a non-existent policy ID."""
    user = {"age": 25, "income": 50_000}
    ok, reason = verify_eligibility(user, "scheme_999")
    assert ok is False
    assert "not found" in reason.lower() or "Policy" in reason


# ─────────────────────────────────────────────────────────────────────────────
# Edge cases
# ─────────────────────────────────────────────────────────────────────────────

def test_empty_profile_defaults():
    """Empty profile should not crash — unknown fields default to safe values."""
    ok, reason = verify_eligibility({}, "scheme_007")
    # age is None → skip age check; no restrictions crash → eligible by default
    assert isinstance(ok, bool)


def test_integer_income_as_string():
    """Income provided as string should be handled (cast to float)."""
    user = {"age": 12, "income": "80000", "community": "Christian"}
    ok, reason = verify_eligibility(user, "scheme_001")
    assert ok is True
