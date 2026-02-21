# app/flow_controller.py

from app.routers import classify_intent
from app.extractor import extract_user_profile, check_missing_fields
from app.memory import ConversationMemory
from app.rule_engine import check_eligibility
from scripts.query_agent import ask_agent


class FlowController:
    """
    Orchestrates full conversational flow.
    """

    def __init__(self):
        self.memory = ConversationMemory()

    async def handle_message(self, message: str) -> str:

        # 1️⃣ Detect Intent
        intent = await classify_intent(message)

        # Casual chat
        if intent == "casual":
            return "Hello 👋 How can I help you with government schemes?"

        # Policy flow
        if intent in ["policy_search", "providing_missing_info"]:

            extracted = await extract_user_profile(message)
            updated_profile = self.memory.merge_profile(extracted)

            missing = check_missing_fields(updated_profile)

            if missing:
                return f"Please provide your {missing[0]}."

            # ✅ Deterministic Rule Engine
            eligibility_result = check_eligibility(updated_profile)

            if eligibility_result["eligible"]:
                rag_result = ask_agent(message)
                return rag_result["answer"]
            else:
                return "You are not eligible based on current scheme criteria."

        # Application flow (future)
        if intent == "application_request":
            return "Application flow not yet connected. (Rule engine + Playwright pending)"

        return "I didn't understand that."

    def reset_conversation(self):
        self.memory.reset()