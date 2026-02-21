"""
logic/eligibility_engine.py
Track-2 Phase 1 — Deterministic Eligibility Engine

All policy rules are encoded as plain Python data (no LLM involvement).
`verify_eligibility` returns a strict (bool, reason_str) tuple — never guesses.
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# Policy Database  (numerical / categorical rules from dummy_data.py)
# Each key is the scheme's `id` field in dummy_data.py.
# ─────────────────────────────────────────────────────────────────────────────
POLICY_DB: dict[str, dict] = {

    # scheme_001 — NSP Pre-Matric Scholarship for Minorities
    "scheme_001": {
        "name": "NSP Pre-Matric Scholarship for Minorities",
        "category": "Scholarship / Education",
        "annual_family_income_max_inr": 100_000,
        "min_age": 0,          # Class 1+, no strict numeric floor
        "max_age": 17,         # up to Class 10 (approx. ≤17 years)
        "allowed_communities": [
            "Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Zoroastrian"
        ],
        "min_attendance_percent": 75,
    },

    # scheme_002 — PM-KISAN
    "scheme_002": {
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "category": "Farming / Agriculture",
        "annual_family_income_max_inr": float("inf"),   # no hard income cap
        "min_age": 18,
        "max_age": 999,
        "must_be_farmer": True,         # must hold cultivable land
        "excluded_occupations": [
            "minister", "mp", "mla", "retired_govt_employee",
            "doctor", "engineer", "lawyer", "chartered_accountant",
            "architect", "income_tax_payer",
        ],
    },

    # scheme_003 — Startup India Seed Fund Scheme (SISFS)
    "scheme_003": {
        "name": "Startup India Seed Fund Scheme (SISFS)",
        "category": "Startup / Entrepreneurship",
        "annual_family_income_max_inr": float("inf"),   # not income-gated
        "min_age": 18,
        "max_age": 999,
        "startup_age_max_years": 2,
        "prior_govt_funding_max_inr": 1_000_000,
        "requires_dpiit": True,
        "allowed_entity_types": [
            "Private Limited Company", "LLP", "Partnership Firm"
        ],
    },

    # scheme_004 — Ayushman Bharat PM-JAY
    "scheme_004": {
        "name": "Ayushman Bharat PM-JAY",
        "category": "Health / Medical",
        "annual_family_income_max_inr": float("inf"),   # SECC-2011 based, not income
        "min_age": 0,
        "max_age": 999,
        "requires_secc_listing": True,   # must appear in SECC-2011 data
    },

    # scheme_005 — PMAY-G (Housing)
    "scheme_005": {
        "name": "Pradhan Mantri Awas Yojana — Gramin (PMAY-G)",
        "category": "Housing / Rural Development",
        "annual_family_income_max_inr": float("inf"),
        "min_age": 18,
        "max_age": 999,
        "requires_secc_listing": True,
        "must_be_rural": True,
        "must_be_houseless_or_kutcha": True,
    },

    # scheme_006 — Mahila Shakti Kendra
    "scheme_006": {
        "name": "Mahila Shakti Kendra (MSK)",
        "category": "Women Empowerment",
        "annual_family_income_max_inr": float("inf"),
        "min_age": 18,
        "max_age": 999,
        "must_be_female": True,
        "must_be_rural": True,
    },

    # scheme_007 — PMKVY 4.0
    "scheme_007": {
        "name": "Pradhan Mantri Kaushal Vikas Yojana (PMKVY 4.0)",
        "category": "Skill Development / Employment",
        "annual_family_income_max_inr": float("inf"),
        "min_age": 18,
        "max_age": 45,
        "must_be_indian": True,
    },

    # scheme_008 — IGNOAPS (Old Age Pension)
    "scheme_008": {
        "name": "Indira Gandhi National Old Age Pension Scheme (IGNOAPS)",
        "category": "Social Security / Pension",
        "annual_family_income_max_inr": float("inf"),   # BPL, not income-threshold
        "min_age": 60,
        "max_age": 999,
        "must_be_bpl": True,
    },

    # scheme_009 — PM SVANidhi (Street Vendor Loan)
    "scheme_009": {
        "name": "PM SVANidhi — PM Street Vendor's AtmaNirbhar Nidhi",
        "category": "MSME / Micro Finance",
        "annual_family_income_max_inr": float("inf"),
        "min_age": 18,
        "max_age": 999,
        "must_be_street_vendor": True,
    },

    # scheme_010 — Post-Matric Scholarship for SC
    "scheme_010": {
        "name": "Post-Matric Scholarship for Scheduled Castes (PMS-SC)",
        "category": "Scholarship / Education",
        "annual_family_income_max_inr": 250_000,
        "min_age": 16,         # Class 11+
        "max_age": 999,
        "allowed_communities": ["Scheduled Caste", "SC"],
        "min_attendance_percent": 75,
    },

    # scheme_011 — PMFBY (Crop Insurance)
    "scheme_011": {
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "category": "Agriculture / Crop Insurance",
        "annual_family_income_max_inr": float("inf"),
        "min_age": 18,
        "max_age": 999,
        "must_be_farmer": True,
    },

    # scheme_012 — PM Surya Ghar (Rooftop Solar)
    "scheme_012": {
        "name": "PM Surya Ghar Muft Bijli Yojana",
        "category": "Energy / Environment",
        "annual_family_income_max_inr": float("inf"),
        "min_age": 18,
        "max_age": 999,
        "must_own_house": True,
        "must_have_electricity_connection": True,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Helper: normalise string inputs (strip, lowercase)
# ─────────────────────────────────────────────────────────────────────────────
def _norm(value: str) -> str:
    return str(value).strip().lower()


# ─────────────────────────────────────────────────────────────────────────────
# Core deterministic engine
# ─────────────────────────────────────────────────────────────────────────────
def verify_eligibility(
    user_profile: dict,
    policy_id: str,
) -> tuple[bool, str]:
    """
    Check whether *user_profile* meets the eligibility rules of *policy_id*.

    Returns
    -------
    (True,  "Eligible")          — all checks passed
    (False, "<specific reason>") — first failing rule, in plain English

    This function is entirely deterministic: no LLM, no randomness, no I/O.
    """
    policy = POLICY_DB.get(policy_id)
    if not policy:
        return False, f"Policy '{policy_id}' not found in the database."

    # ── 1. Age check ──────────────────────────────────────────────────────────
    age = user_profile.get("age")
    if age is not None:
        age = int(age)
        if age < policy.get("min_age", 0):
            return (
                False,
                f"Age is below the minimum requirement of {policy['min_age']}.",
            )
        if age > policy.get("max_age", 999):
            return (
                False,
                f"Age exceeds the maximum limit of {policy['max_age']} for this scheme.",
            )

    # ── 2. Income check ───────────────────────────────────────────────────────
    income = user_profile.get("income")
    limit = policy.get("annual_family_income_max_inr", float("inf"))
    if income is not None and limit != float("inf"):
        if float(income) > limit:
            return (
                False,
                f"Annual family income ₹{income:,} exceeds the maximum allowed "
                f"limit of ₹{int(limit):,} for this scheme.",
            )

    # ── 3. Community / caste check ────────────────────────────────────────────
    allowed_communities = policy.get("allowed_communities")
    if allowed_communities:
        user_community = user_profile.get("community", "")
        if not any(
            _norm(user_community) == _norm(c) for c in allowed_communities
        ):
            return (
                False,
                f"Community '{user_community}' is not eligible. "
                f"Allowed communities: {', '.join(allowed_communities)}.",
            )

    # ── 4. Attendance check ───────────────────────────────────────────────────
    min_att = policy.get("min_attendance_percent")
    if min_att is not None:
        user_att = user_profile.get("attendance_percent")
        if user_att is not None and float(user_att) < min_att:
            return (
                False,
                f"Attendance {user_att}% is below the required {min_att}%.",
            )

    # ── 5. Farmer requirement ─────────────────────────────────────────────────
    if policy.get("must_be_farmer"):
        if not user_profile.get("is_farmer", False):
            return False, "Applicant must be a land-holding farmer for this scheme."
        # Excluded occupations for PM-KISAN
        excluded = policy.get("excluded_occupations", [])
        user_occ = _norm(user_profile.get("occupation", ""))
        for occ in excluded:
            if _norm(occ) in user_occ or user_occ in _norm(occ):
                return (
                    False,
                    f"Occupation '{user_profile.get('occupation')}' is in the "
                    f"excluded category for this scheme.",
                )

    # ── 6. Street vendor requirement ──────────────────────────────────────────
    if policy.get("must_be_street_vendor"):
        if not user_profile.get("is_street_vendor", False):
            return False, "Applicant must be a registered street vendor for PM SVANidhi."

    # ── 7. Gender requirement ─────────────────────────────────────────────────
    if policy.get("must_be_female"):
        if _norm(user_profile.get("gender", "")) not in ("female", "f", "woman"):
            return False, "This scheme is exclusively for women (rural)."

    # ── 8. Rural requirement ──────────────────────────────────────────────────
    if policy.get("must_be_rural"):
        if not user_profile.get("is_rural", False):
            return False, "Applicant must reside in a rural area for this scheme."

    # ── 9. BPL requirement ────────────────────────────────────────────────────
    if policy.get("must_be_bpl"):
        if not user_profile.get("is_bpl", False):
            return False, "Applicant must belong to a Below Poverty Line (BPL) household."

    # ── 10. SECC-2011 listing requirement ─────────────────────────────────────
    if policy.get("requires_secc_listing"):
        if not user_profile.get("secc_listed", False):
            return (
                False,
                "Applicant must be listed in the SECC-2011 socio-economic database.",
            )

    # ── 11. House ownership requirement ──────────────────────────────────────
    if policy.get("must_own_house"):
        if not user_profile.get("owns_house", False):
            return False, "Applicant must own a residential house with a suitable rooftop."

    # ── 12. Electricity connection requirement ────────────────────────────────
    if policy.get("must_have_electricity_connection"):
        if not user_profile.get("has_electricity_connection", False):
            return False, "Applicant must have a valid electricity consumer connection."

    # ── 13. Startup-specific checks ───────────────────────────────────────────
    startup_age = policy.get("startup_age_max_years")
    if startup_age is not None:
        user_startup_age = user_profile.get("startup_age_years")
        if user_startup_age is not None and float(user_startup_age) > startup_age:
            return (
                False,
                f"Startup age {user_startup_age} years exceeds the maximum "
                f"allowed {startup_age} years from incorporation.",
            )

    prior_funding = policy.get("prior_govt_funding_max_inr")
    if prior_funding is not None:
        user_funding = user_profile.get("prior_govt_funding_inr", 0)
        if float(user_funding) > prior_funding:
            return (
                False,
                f"Prior government funding ₹{user_funding:,} exceeds the "
                f"allowed ceiling of ₹{int(prior_funding):,}.",
            )

    if policy.get("requires_dpiit"):
        if not user_profile.get("dpiit_recognised", False):
            return (
                False,
                "Startup must have DPIIT recognition. "
                "Register at startupindia.gov.in first.",
            )

    # ── All checks passed ─────────────────────────────────────────────────────
    return True, "Eligible"
