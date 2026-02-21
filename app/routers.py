# app/routers.py

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()

# Create lightweight classifier LLM
llm_classifier = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)


async def classify_intent(user_message: str) -> str:
    """
    Classifies user intent into one of the predefined categories.
    
    Returns:
        str: one of ["casual", "policy_search", "providing_missing_info", "application_request"]
    """

    prompt = f"""
You are an intent classification system.

Classify the user message into ONE of these labels:
- casual
- policy_search
- providing_missing_info
- application_request

Rules:
- Greetings → casual
- Asking about scheme eligibility → policy_search
- Providing age/income/category details → providing_missing_info
- Asking to apply / fill form → application_request

User Message:
{user_message}

Respond with ONLY the label.
"""

    response = llm_classifier.invoke(
        [HumanMessage(content=prompt)]
    )

    intent = response.content.strip().lower()

    # Safety fallback
    allowed = [
        "casual",
        "policy_search",
        "providing_missing_info",
        "application_request",
    ]

    if intent not in allowed:
        return "casual"

    return intent