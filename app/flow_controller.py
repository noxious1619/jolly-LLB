# app/flow_controller.py

from app.routers import classify_intent
from app.extractor import extract_user_profile, check_missing_fields
from app.memory import ConversationMemory
from scripts.query_agent import ask_agent


class FlowController:
    """
    Orchestrates full Track-1 conversational flow.
    """

    def __init__(self):
        self.memory = ConversationMemory()

    async def handle_message(self, message: str) -> str:

        # 1️⃣ Detect Intent
        intent = await classify_intent(message)

        # Casual Chat
        if intent == "casual":
            return "Hello 👋 How can I help you with government schemes?"

        # Policy search or providing info
        if intent in ["policy_search", "providing_missing_info"]:

            extracted = await extract_user_profile(message)
            updated_profile = self.memory.merge_profile(extracted)

            missing = check_missing_fields(updated_profile)

            if missing:
                return f"Please provide your {missing[0]}."

            # Profile complete → Trigger RAG
            rag_result = ask_agent(message)
            return rag_result["answer"]

        # Application request (future integration)
        if intent == "application_request":
            return "Application flow not yet connected. (Rule engine + Playwright pending)"

        return "I didn't understand that."

    def reset_conversation(self):
        self.memory.reset()