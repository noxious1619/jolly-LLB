# app/rule_engine.py

from app.extractor import UserProfile
from data.dummy_data import SCHEMES


def check_eligibility(profile: UserProfile) -> dict:
    """
    Deterministically checks user eligibility against dummy schemes.
    Returns:
        {
            "eligible": True/False,
            "matched_scheme": scheme_dict_or_None
        }
    """

    profile_data = profile.model_dump()

    age = profile_data.get("age")
    income = profile_data.get("annual_income")

    for scheme in SCHEMES:

        eligibility = scheme.get("eligibility", {})

        # Example Rule: income-based check
        max_income = eligibility.get("annual_family_income_max_inr")

        if max_income:
            if income and income <= max_income:
                return {
                    "eligible": True,
                    "matched_scheme": scheme
                }

    return {
        "eligible": False,
        "matched_scheme": None
    }