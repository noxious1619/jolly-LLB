# app/extractor.py

import os
from typing import Optional, List
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# ---------------------------
# 1️⃣ Define Structured Schema
# ---------------------------

class UserProfile(BaseModel):
    age: Optional[int] = None
    annual_income: Optional[int] = None
    community: Optional[str] = None
    class_level: Optional[int] = None
    land_owned_acres: Optional[float] = None
    target_scheme: Optional[str] = None


# ---------------------------
# 2️⃣ Setup LLM
# ---------------------------

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

parser = JsonOutputParser(pydantic_object=UserProfile)

prompt = PromptTemplate(
    template="""
Extract structured user information from the message below.

If a field is not mentioned, return null.

{format_instructions}

User Message:
{message}
""",
    input_variables=["message"],
    partial_variables={
        "format_instructions": parser.get_format_instructions(),
    },
)

chain = prompt | llm | parser


# ---------------------------
# 3️⃣ Extract Function
# ---------------------------

async def extract_user_profile(message: str) -> UserProfile:
    """
    Extract structured user data from free text.
    Ensures output is always a UserProfile object.
    """

    result = chain.invoke({"message": message})

    # If already dict, convert to UserProfile
    if isinstance(result, dict):
        return UserProfile(**result)

    return result


# ---------------------------
# 4️⃣ Missing Field Checker
# ---------------------------

def check_missing_fields(profile: UserProfile) -> List[str]:
    """
    Returns list of missing required fields.
    """
    required_fields = [
        "age",
        "annual_income",
    ]

    missing = []

    profile_dict = profile.model_dump()

    for field in required_fields:
        if profile_dict.get(field) is None:
            missing.append(field)

    return missing