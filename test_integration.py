# test_integration.py
# Integration test for the full Track-1 + Track-2 pipeline.
# Uses unittest.mock to stub external API calls (Groq, Gemini, FAISS).
# Run: python -m pytest test_integration.py -v

import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

from app.flow_controller import FlowController


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def run(coro):
    """Run a coroutine synchronously. Uses asyncio.run() for Python 3.10+ compatibility."""
    return asyncio.run(coro)


def make_mock_faiss(docs=None):
    """Return a mock FAISS db that returns predictable documents."""
    from langchain_core.documents import Document
    if docs is None:
        docs = [
            Document(
                page_content="NSP Scholarship for minority students",
                metadata={
                    "scheme_id": "scheme_001",
                    "title": "NSP Pre-Matric Scholarship for Minorities",
                    "category": "Scholarship",
                    "max_income_inr": 100000.0,
                    "min_age": 0,
                    "max_age": 17,
                },
            )
        ]
    mock_db = MagicMock()
    mock_db.similarity_search.return_value = docs
    return mock_db


# ─────────────────────────────────────────────────────────────
# Test Class
# ─────────────────────────────────────────────────────────────
class TestFlowControllerIntegration(unittest.TestCase):

    def setUp(self):
        """Fresh controller for each test."""
        self.flow = FlowController()

    # ── Test 1: Casual greeting ────────────────────────────────────────────────
    @patch("app.routers.llm_classifier")
    def test_casual_returns_greeting(self, mock_llm):
        mock_llm.invoke.return_value = MagicMock(content="casual")
        reply = run(self.flow.handle_message("Hi there!"))
        self.assertIn("JOLLY-LLB", reply)
        self.assertIn("Citizen Advocate", reply)

    # ── Test 2: Missing age → asks for age ───────────────────────────────────
    @patch("app.flow_controller._get_faiss_db")
    @patch("app.flow_controller.ask_agent")
    @patch("app.flow_controller.extract_user_profile")
    @patch("app.routers.llm_classifier")
    def test_missing_age_asks_question(
        self, mock_llm, mock_extract, mock_rag, mock_faiss
    ):
        mock_llm.invoke.return_value = MagicMock(content="policy_search")
        mock_extract.return_value = AsyncMock(return_value=MagicMock(
            age=None,
            annual_income=None,
            community="Muslim",
            target_scheme_id="scheme_001",
            target_scheme=None,
            to_logic_profile=lambda: {},
            model_dump=lambda: {},
        ))()

        from app.extractor import UserProfile
        mock_extract.side_effect = None
        mock_extract.return_value = UserProfile(
            community="Muslim",
            target_scheme="minority scholarship",
        )

        async def _extract(msg):
            return UserProfile(community="Muslim", target_scheme="minority scholarship")

        with patch("app.flow_controller.extract_user_profile", _extract):
            reply = run(self.flow.handle_message("Main minority student hoon"))

        self.assertIn("age", reply.lower())

    # ── Test 3: Eligible profile → Track-2 success + Track-1 LLM ────────────
    @patch("app.flow_controller._get_faiss_db", return_value=make_mock_faiss())
    @patch("app.flow_controller.ask_agent")
    @patch("app.flow_controller.extract_user_profile")
    @patch("app.routers.llm_classifier")
    def test_eligible_profile_calls_rag(
        self, mock_llm, mock_extract, mock_rag, mock_faiss
    ):
        mock_llm.invoke.return_value = MagicMock(content="providing_missing_info")
        mock_rag.return_value = {
            "answer": "You qualify! Apply at scholarships.gov.in",
            "sources": ["NSP Pre-Matric Scholarship for Minorities"],
        }

        from app.extractor import UserProfile

        async def _extract(msg):
            return UserProfile(age=14, annual_income=80000, community="Muslim")

        # Pre-seed memory with scheme target
        self.flow.memory.profile = UserProfile(
            age=14, annual_income=80000, community="Muslim",
            target_scheme="minority scholarship",
        )

        with patch("app.flow_controller.extract_user_profile", _extract):
            reply = run(self.flow.handle_message("Meri income 80000 hai"))

        self.assertIn("eligible", reply.lower())
        mock_rag.assert_called_once()

    # ── Test 4: Ineligible → NBA redirect returned, LLM explains alternative ─
    @patch("app.flow_controller._get_faiss_db", return_value=make_mock_faiss())
    @patch("app.flow_controller.ask_agent")
    @patch("app.flow_controller.extract_user_profile")
    @patch("app.routers.llm_classifier")
    def test_ineligible_triggers_nba(
        self, mock_llm, mock_extract, mock_rag, mock_faiss
    ):
        mock_llm.invoke.return_value = MagicMock(content="providing_missing_info")
        mock_rag.return_value = {
            "answer": "NSP Pre-Matric Scholarship info here.",
            "sources": ["NSP Pre-Matric Scholarship for Minorities"],
        }

        from app.extractor import UserProfile

        async def _extract(msg):
            return UserProfile(age=25, annual_income=500000, community="Hindu")

        # High income + wrong community → ineligible for scheme_001
        self.flow.memory.profile = UserProfile(
            age=25, annual_income=500000, community="Hindu",
            target_scheme="minority scholarship",
        )

        with patch("app.flow_controller.extract_user_profile", _extract):
            reply = run(self.flow.handle_message("My income is 5 lakh"))

        # Should mention not eligible OR redirect
        self.assertTrue(
            "not eligible" in reply.lower()
            or "redirect" in reply.lower()
            or "❌" in reply
            or "however" in reply.lower()
            or "apply for" in reply.lower()
        )

    # ── Test 5: Eligibility engine unit — verify directly ────────────────────
    def test_eligibility_engine_eligible(self):
        from logic.eligibility_engine import verify_eligibility
        ok, reason = verify_eligibility(
            {"age": 14, "income": 80000, "community": "Muslim"}, "scheme_001"
        )
        self.assertTrue(ok)
        self.assertEqual(reason, "Eligible")

    def test_eligibility_engine_income_too_high(self):
        from logic.eligibility_engine import verify_eligibility
        ok, reason = verify_eligibility(
            {"age": 14, "income": 200000, "community": "Muslim"}, "scheme_001"
        )
        self.assertFalse(ok)
        self.assertIn("income", reason.lower())

    def test_eligibility_engine_wrong_community(self):
        from logic.eligibility_engine import verify_eligibility
        ok, reason = verify_eligibility(
            {"age": 14, "income": 80000, "community": "Hindu"}, "scheme_001"
        )
        self.assertFalse(ok)
        self.assertIn("community", reason.lower())

    # ── Test 6: SCHEME_NAME_MAP resolution ───────────────────────────────────
    def test_scheme_name_map_resolves_correctly(self):
        from app.extractor import resolve_scheme_id
        self.assertEqual(resolve_scheme_id("minority scholarship"), "scheme_001")
        self.assertEqual(resolve_scheme_id("PM KISAN"), "scheme_002")
        self.assertEqual(resolve_scheme_id("startup india"), "scheme_003")
        self.assertEqual(resolve_scheme_id("kisan"), "scheme_002")
        self.assertIsNone(resolve_scheme_id("xyz unknown scheme"))

    # ── Test 7: to_logic_profile() key mapping ────────────────────────────────
    def test_to_logic_profile_maps_keys(self):
        from app.extractor import UserProfile
        profile = UserProfile(age=22, annual_income=90000, community="Christian")
        lp = profile.to_logic_profile()
        self.assertEqual(lp["age"], 22)
        self.assertEqual(lp["income"], 90000)
        self.assertEqual(lp["community"], "Christian")
        self.assertIn("has_electricity_connection", lp)


if __name__ == "__main__":
    unittest.main(verbosity=2)
