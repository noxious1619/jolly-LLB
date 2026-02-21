"""
logic/next_best_action.py
Track-2 Phase 2 — Next Best Action (NBA) Retrieval Layer

If a user is rejected by the deterministic eligibility engine, this module
silently queries the FAISS vector store to find an alternative scheme they
*actually* qualify for — using metadata filtering and semantic similarity.
"""

from __future__ import annotations

from typing import Any

from .eligibility_engine import verify_eligibility


# ─────────────────────────────────────────────────────────────────────────────
# Metadata-based candidate filtering
# ─────────────────────────────────────────────────────────────────────────────
def _profile_passes_metadata(user_profile: dict, metadata: dict) -> bool:
    """
    Fast pre-filter on FAISS document metadata before calling verify_eligibility.
    Returns True if the candidate scheme *could* accommodate this user based on
    purely numeric fields stored in the FAISS metadata dict.
    """
    # Income gate
    max_income = metadata.get("max_income_inr", float("inf"))
    user_income = float(user_profile.get("income", 0))
    if max_income != float("inf") and user_income > max_income:
        return False

    # Age gates
    min_age = metadata.get("min_age", 0)
    max_age = metadata.get("max_age", 999)
    user_age = user_profile.get("age")
    if user_age is not None:
        user_age = int(user_age)
        if user_age < min_age or user_age > max_age:
            return False

    return True


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────
def handle_policy_request(
    user_profile: dict,
    target_policy_id: str,
    faiss_db: Any,                # langchain FAISS instance
    query_text: str = "government financial assistance scheme India",
    n_candidates: int = 8,
) -> dict:
    """
    Orchestrate the full Track-2 flow for one policy request.

    1. Run the deterministic eligibility engine against *target_policy_id*.
    2. If eligible → return success immediately.
    3. If rejected → intercept the failure; query FAISS for *n_candidates*
       similar schemes; filter by metadata; run eligibility engine on each
       candidate; return the first passing alternative.

    Parameters
    ----------
    user_profile       : dict with keys like age, income, community, is_farmer, …
    target_policy_id   : e.g. "scheme_001"
    faiss_db           : a LangChain FAISS vector store (already loaded)
    query_text         : semantic query used to seed the FAISS search
    n_candidates       : how many FAISS docs to retrieve before filtering

    Returns
    -------
    {
      "status":      "success" | "redirect" | "failed",
      "message":     <human-readable explanation>,
      "reason":      <rejection reason from Phase 1, or None>,
      "alternative": {
          "scheme_id":   "scheme_XXX",
          "name":        "...",
          "category":    "...",
      } | None,
    }
    """

    # ── Phase 1 Gate ──────────────────────────────────────────────────────────
    is_eligible, reason = verify_eligibility(user_profile, target_policy_id)

    if is_eligible:
        return {
            "status": "success",
            "message": (
                f"✅ You are eligible for scheme '{target_policy_id}'. "
                "Let's proceed with the application!"
            ),
            "reason": None,
            "alternative": None,
        }

    # ── Phase 2: Intercept & Redirect ─────────────────────────────────────────
    print(
        f"[NBA] Rejected '{target_policy_id}': {reason}. "
        "Triggering Next Best Action query..."
    )

    # Semantic search — retrieve a pool of candidate documents from FAISS
    try:
        candidate_docs = faiss_db.similarity_search(query_text, k=n_candidates)
    except Exception as exc:
        return {
            "status": "failed",
            "message": f"FAISS retrieval error: {exc}",
            "reason": reason,
            "alternative": None,
        }

    # Walk candidates (ranked by semantic similarity) and test eligibility
    for doc in candidate_docs:
        meta = doc.metadata or {}
        candidate_id = meta.get("scheme_id", "")

        # Skip the originally requested scheme
        if candidate_id == target_policy_id:
            continue

        # Fast pre-filter using metadata numerics
        if not _profile_passes_metadata(user_profile, meta):
            continue

        # Full deterministic check on the candidate
        alt_eligible, _ = verify_eligibility(user_profile, candidate_id)
        if alt_eligible:
            alt_name = meta.get("title", candidate_id)
            alt_category = meta.get("category", "")
            return {
                "status": "redirect",
                "message": (
                    f"❌ You are not eligible for '{target_policy_id}' — {reason}\n"
                    f"🔄 However, based on your profile, you can apply for:\n"
                    f"   📋 **{alt_name}** ({alt_category})"
                ),
                "reason": reason,
                "alternative": {
                    "scheme_id": candidate_id,
                    "name": alt_name,
                    "category": alt_category,
                },
            }

    # No suitable alternative found
    return {
        "status": "failed",
        "message": (
            f"❌ You are not eligible for '{target_policy_id}' — {reason}\n"
            "😔 No suitable alternative schemes were found for your profile at this time."
        ),
        "reason": reason,
        "alternative": None,
    }
