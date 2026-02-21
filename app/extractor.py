# app/extractor.py
# Track 1 — Structured Profile Extraction
# Extracts user fields from free text via Groq LLM.
# The `to_logic_profile()` method bridges to Track-2 (logic/).

import os
from typing import Optional, List
from dotenv import load_dotenv
from pydantic import BaseModel, model_validator
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

load_dotenv()

# ─────────────────────────────────────────────────────────────
# Scheme name → scheme_id mapping (natural language → logic DB)
# ─────────────────────────────────────────────────────────────
SCHEME_NAME_MAP: dict[str, str] = {
    # Scholarships
    "scholarship":          "scheme_001",
    "nsp":                  "scheme_001",
    "pre-matric":           "scheme_001",
    "minority":             "scheme_001",
    "minority scholarship": "scheme_001",
    "post matric":          "scheme_010",
    "post-matric":          "scheme_010",
    "sc scholarship":       "scheme_010",
    "scheduled caste":      "scheme_010",
    # Agriculture
    "pm kisan":             "scheme_002",
    "pmkisan":              "scheme_002",
    "kisan":                "scheme_002",
    "farmer":               "scheme_002",
    "fasal bima":           "scheme_011",
    "pmfby":                "scheme_011",
    "crop insurance":       "scheme_011",
    # Startup
    "startup":              "scheme_003",
    "sisfs":                "scheme_003",
    "seed fund":            "scheme_003",
    "startup india":        "scheme_003",
    # Health
    "ayushman":             "scheme_004",
    "pm-jay":               "scheme_004",
    "health insurance":     "scheme_004",
    # Housing
    "pmay":                 "scheme_005",
    "housing":              "scheme_005",
    "awas":                 "scheme_005",
    # Women
    "mahila":               "scheme_006",
    "women":                "scheme_006",
    # Skill
    "pmkvy":                "scheme_007",
    "skill":                "scheme_007",
    "training":             "scheme_007",
    # Pension
    "pension":              "scheme_008",
    "ignoaps":              "scheme_008",
    "old age":              "scheme_008",
    # Street vendor
    "svanidhi":             "scheme_009",
    "street vendor":        "scheme_009",
    "vendor":               "scheme_009",
    # Solar
    "surya ghar":           "scheme_012",
    "solar":                "scheme_012",
    "rooftop":              "scheme_012",
}


def resolve_scheme_id(scheme_name: Optional[str]) -> Optional[str]:
    """
    Map a natural-language scheme name (from the LLM) to a POLICY_DB scheme_id.
    Returns None if no match found (caller should default to scheme_001 or ask user).
    """
    if not scheme_name:
        return None
    lower = scheme_name.strip().lower()
    # Exact key match first
    if lower in SCHEME_NAME_MAP:
        return SCHEME_NAME_MAP[lower]
    # Substring match
    for keyword, sid in SCHEME_NAME_MAP.items():
        if keyword in lower or lower in keyword:
            return sid
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 1. Pydantic Schema — UserProfile
# ─────────────────────────────────────────────────────────────────────────────
class UserProfile(BaseModel):
    """
    Structured snapshot of the citizen's demographic/financial details,
    collected incrementally across conversation turns.
    """
    # Core identifiers
    age:                Optional[int]   = None
    annual_income:      Optional[int]   = None   # in INR
    community:          Optional[str]   = None   # Muslim / SC / General …
    class_level:        Optional[int]   = None   # school class (1–12)
    land_owned_acres:   Optional[float] = None

    # Lifestyle flags (for PM-KISAN, PM SVANidhi, etc.)
    is_farmer:          Optional[bool]  = None
    is_street_vendor:   Optional[bool]  = None
    is_rural:           Optional[bool]  = None
    is_bpl:             Optional[bool]  = None
    secc_listed:        Optional[bool]  = None
    gender:             Optional[str]   = None   # male / female / other
    owns_house:         Optional[bool]  = None
    has_electricity:    Optional[bool]  = None
    occupation:         Optional[str]   = None

    # Startup-specific
    dpiit_recognised:       Optional[bool]  = None
    startup_age_years:      Optional[float] = None
    prior_govt_funding_inr: Optional[int]   = None

    # Scheme targeting
    target_scheme:    Optional[str] = None   # free-text name from user
    target_scheme_id: Optional[str] = None   # resolved POLICY_DB ID

    @model_validator(mode="after")
    def resolve_target_id(self) -> "UserProfile":
        """Auto-resolve target_scheme_id whenever target_scheme is set."""
        if self.target_scheme and not self.target_scheme_id:
            self.target_scheme_id = resolve_scheme_id(self.target_scheme)
        return self

    # ── Bridge to logic/ layer ────────────────────────────────────────────────
    def to_logic_profile(self) -> dict:
        """
        Convert UserProfile to the flat dict format expected by
        logic/eligibility_engine.verify_eligibility().

        Key mapping:
          annual_income → income
          has_electricity → has_electricity_connection
        """
        return {
            "age":                       self.age,
            "income":                    self.annual_income,
            "community":                 self.community,
            "is_farmer":                 self.is_farmer or False,
            "is_street_vendor":          self.is_street_vendor or False,
            "is_rural":                  self.is_rural or False,
            "is_bpl":                    self.is_bpl or False,
            "secc_listed":               self.secc_listed or False,
            "gender":                    self.gender or "",
            "owns_house":                self.owns_house or False,
            "has_electricity_connection": self.has_electricity or False,
            "occupation":                self.occupation or "",
            "dpiit_recognised":          self.dpiit_recognised or False,
            "startup_age_years":         self.startup_age_years,
            "prior_govt_funding_inr":    self.prior_govt_funding_inr or 0,
        }


# ─────────────────────────────────────────────────────────────────────────────
# 2. LLM Extraction Chain
# ─────────────────────────────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

parser = JsonOutputParser(pydantic_object=UserProfile)

prompt = PromptTemplate(
    template="""Extract structured citizen information from the message below.
Return null for any field not mentioned. Do NOT guess or infer.

{format_instructions}

User Message:
{message}
""",
    input_variables=["message"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

extraction_chain = prompt | llm | parser


# ─────────────────────────────────────────────────────────────────────────────
# 3. Public Functions
# ─────────────────────────────────────────────────────────────────────────────
async def extract_user_profile(message: str) -> UserProfile:
    """Extract a UserProfile from a free-text message using Groq LLM."""
    try:
        result = extraction_chain.invoke({"message": message})
        if isinstance(result, dict):
            return UserProfile(**result)
        return result
    except Exception:
        return UserProfile()


def check_missing_fields(profile: UserProfile, scheme_id: Optional[str] = None) -> List[str]:
    """
    Return list of critical missing fields for the given scheme.

    Always requires age + annual_income.
    scheme_001 (minorities scholarship) also requires community.
    """
    missing: List[str] = []

    if profile.age is None:
        missing.append("age")
    if profile.annual_income is None:
        missing.append("annual income")

    # Community required for minority/SC scholarship schemes
    if scheme_id in ("scheme_001", "scheme_010") and profile.community is None:
        missing.append("community/caste category")

    return missing