# app/flow_controller.py
# Orchestrates the full JOLLY-LLB conversational pipeline.
#
# Turn-by-turn flow:
#   1. classify_intent()      → route (casual | policy_search | …)
#   2. extract_user_profile() → parse structured fields from message
#   3. memory.merge_profile() → accumulate fields across turns
#   4. check_missing_fields() → ask for critical info before gating
#   5. [TRACK-2] handle_policy_request() → deterministic eligibility gate
#   6. [TRACK-1] ask_agent()  → RAG retrieval + Groq LLM explanation
#   7. Return combined NBA verdict + LLM answer

from __future__ import annotations

import os
from functools import lru_cache

from app.routers import classify_intent
from app.extractor import extract_user_profile, check_missing_fields, UserProfile
from app.memory import ConversationMemory

# Track-2: deterministic gate + Next Best Action
from logic.next_best_action import handle_policy_request

# Track-1: FAISS retrieval + Groq LLM answer
from scripts.query_agent import ask_agent, load_vector_db

# Default scheme when the user hasn't named one yet
_DEFAULT_SCHEME_ID = "scheme_001"


@lru_cache(maxsize=1)
def _get_faiss_db():
    """
    Load FAISS index once and cache it for the lifetime of the process.
    Raises FileNotFoundError if ingest.py hasn't been run yet.
    """
    return load_vector_db()


def _nba_message(nba: dict) -> str:
    """Format the Track-2 NBA result into a citizen-friendly header."""
    status = nba["status"]
    if status == "success":
        return "✅ " + nba["message"]
    if status == "redirect":
        return nba["message"]
    # failed — no alternative found
    return nba["message"]


class FlowController:
    """
    Orchestrates the full conversational flow across multiple turns.
    Maintains a per-session ConversationMemory.
    """

    def __init__(self):
        self.memory = ConversationMemory()

    async def handle_message(self, message: str) -> str:
        # ── Step 1: Intent classification ─────────────────────────────────────
        intent = await classify_intent(message)

        # ── Casual / off-topic ─────────────────────────────────────────────────
        if intent == "casual":
            return (
                "👋 Hello! I'm **JOLLY-LLB**, your Citizen Advocate AI.\n"
                "I can help you find and apply for Indian government schemes "
                "(scholarships, PM-KISAN, Startup India, and more).\n\n"
                "Tell me what you're looking for and a bit about yourself "
                "(age, income, community), and I'll check your eligibility!"
            )

        # ── Application request (future Playwright integration) ────────────────
        if intent == "application_request":
            return (
                "📝 Application assistance is coming soon!\n"
                "For now, I can check your eligibility and give you the exact "
                "portal URL and step-by-step instructions to apply yourself."
            )

        # ── Policy flow: policy_search | providing_missing_info ────────────────
        if intent in ("policy_search", "providing_missing_info"):

            # Step 2: Extract fields from this message
            extracted = await extract_user_profile(message)

            # Step 3: Merge into session memory
            updated_profile: UserProfile = self.memory.merge_profile(extracted)

            # Resolve target scheme ID (use memory-accumulated target_scheme_id)
            target_id = updated_profile.target_scheme_id or _DEFAULT_SCHEME_ID

            # Step 4: Ask for missing critical fields before running gates
            missing = check_missing_fields(updated_profile, scheme_id=target_id)
            if missing:
                field = missing[0]
                friendly = {
                    "age":                   "What is your age?",
                    "annual income":         "What is your annual family income (in rupees)?",
                    "community/caste category": (
                        "Which community do you belong to? "
                        "(e.g., Muslim, Christian, Sikh, SC, General)"
                    ),
                }.get(field, f"Could you please provide your {field}?")
                return f"❓ {friendly}"

            # Step 5 — TRACK-2: Deterministic eligibility gate + NBA
            logic_profile = updated_profile.to_logic_profile()

            try:
                faiss_db = _get_faiss_db()
            except FileNotFoundError:
                return (
                    "⚠️ The knowledge base isn't set up yet. "
                    "Please run `python ingest.py` first, then try again."
                )

            nba = handle_policy_request(
                user_profile=logic_profile,
                target_policy_id=target_id,
                faiss_db=faiss_db,
            )

            # Step 6 — TRACK-1: RAG retrieval + Groq LLM explanation
            # If NBA found an alternative, steer the LLM toward it
            if nba["status"] == "redirect" and nba.get("alternative"):
                alt = nba["alternative"]
                rag_query = (
                    f"Explain the '{alt['name']}' scheme in detail. "
                    f"What are the eligibility criteria, benefits, and "
                    f"how can a citizen apply? Original question: {message}"
                )
            else:
                rag_query = message

            try:
                rag_result = ask_agent(rag_query)
                llm_answer = rag_result["answer"]
                sources = rag_result.get("sources", [])
            except Exception as exc:
                llm_answer = f"(Could not generate LLM response: {exc})"
                sources = []

            # Step 7: Combine NBA verdict + LLM answer
            header = _nba_message(nba)
            source_line = ""
            if sources:
                source_line = f"\n\n📚 *Sources: {', '.join(sources)}*"

            # For success, show LLM answer after the eligibility confirmation
            # For redirect, LLM will explain the alternative scheme
            # For failed, just show the NBA message (no useful scheme to explain)
            if nba["status"] == "failed":
                return header
            else:
                return f"{header}\n\n---\n\n{llm_answer}{source_line}"

        # Fallback
        return "I didn't quite understand that. Could you rephrase?"

    def reset_conversation(self):
        """Clear session memory (called by /reset endpoint)."""
        self.memory.reset()