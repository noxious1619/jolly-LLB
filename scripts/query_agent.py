
import os
from typing import List
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.embeddings import Embeddings

load_dotenv()

# ── Custom Embeddings class using google.generativeai REST API ──────────────
# Bypasses the broken gRPC/v1beta path in the installed langchain-google-genai.
class GeminiEmbeddings(Embeddings):
    """LangChain-compatible embeddings via google.generativeai REST API."""

    def __init__(self, model: str = "models/text-embedding-004"):
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [
            genai.embed_content(model=self.model, content=text)["embedding"]
            for text in texts
        ]

    def embed_query(self, text: str) -> List[float]:
        return genai.embed_content(model=self.model, content=text)["embedding"]

# ─────────────────────────────────────────────
# SYSTEM PROMPT — Citizen Advocate Personality
# ─────────────────────────────────────────────
CITIZEN_ADVOCATE_SYSTEM_PROMPT = """
You are **JOLLY-LLB**, a trusted Citizen Advocate AI assistant powered by the Zynd Protocol.
Your mission is to make Indian government policies simple, accessible, and actionable for every citizen.

## Your Core Responsibilities:
1. **Policy Summary (Hinglish):** Always summarize the policy in simple, friendly Hinglish (Hindi + English mix).
   - Use easy-to-understand language. Avoid complex legal jargon.
   - Example tone: "Yeh scheme farmers ke liye hai jo Rs. 6,000 per saal deti hai seedhe bank mein."

2. **Explicit Eligibility Check:** Clearly state WHO qualifies and WHO does NOT.
   - List income limits, age range, category restrictions, and land/profession requirements.

3. **Ask for Missing Details:** If the user hasn't told you their income, age, category (SC/ST/OBC/Minority),
   or land holding, POLITELY ASK these follow-up questions before giving a final eligibility verdict.
   - Example: "Aapki annual family income kitni hai? Aur aap kis community se belong karte hain?"

4. **Next Steps:** Always end with clear, numbered "NEXT STEPS" for how to apply — including the portal URL.

5. **Trust Signal:** End each response with: "✅ Verified by JOLLY-LLB via Zynd Protocol — Trustworthy Information."

## Formatting Rules:
- Use bullet points and numbered lists for clarity.
- Use emojis sparingly but effectively: 📋 for eligibility, 💰 for benefits, 📝 for steps, ❓ for questions.
- Always respond in the language mix the user prefers (Hindi, English, or Hinglish).

## Retrieved Context:
{context}

## Citizen's Question:
{question}

## Your Response (as JOLLY-LLB, Citizen Advocate):
"""

CITIZEN_ADVOCATE_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=CITIZEN_ADVOCATE_SYSTEM_PROMPT,
)


def load_vector_db() -> Chroma:
    """Load the existing ChromaDB vector store."""
    embeddings = GeminiEmbeddings(model="models/text-embedding-004")
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vector_db")
    vector_db = Chroma(
        persist_directory=db_path,
        embedding_function=embeddings,
    )
    return vector_db


def build_qa_chain(vector_db: Chroma) -> RetrievalQA:
    """Build the LangChain RetrievalQA chain with the Citizen Advocate prompt."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.3,           
        convert_system_message_to_human=True,
    )
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3},
        ),
        chain_type_kwargs={"prompt": CITIZEN_ADVOCATE_PROMPT},
        return_source_documents=True,
    )
    return qa_chain


def ask_agent(user_query: str) -> dict:
    """
    Main entry point: given a user question, return the agent's answer
    and the source scheme documents used for context.

    Returns:
        {
            "answer": str,
            "sources": list[str]   # scheme titles retrieved
        }
    """
    vector_db = load_vector_db()
    qa_chain = build_qa_chain(vector_db)

    result = qa_chain.invoke({"query": user_query})

    # Extract unique source scheme names
    sources = list({
        doc.metadata.get("title", "Unknown Scheme")
        for doc in result.get("source_documents", [])
    })

    return {
        "answer": result["result"],
        "sources": sources,
    }


def interactive_session():
    """Run an interactive CLI session with the Citizen Advocate."""
    print("\n" + "═" * 60)
    print("  🇮🇳  POLICY-NAVIGATOR — Citizen Advocate (JOLLY-LLB)")
    print("  Powered by Zynd Protocol + Gemini 2.5 Pro")
    print("═" * 60)
    print("  Type your question in Hindi, English, or Hinglish.")
    print("  Type 'exit' or 'quit' to end the session.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nJOLLY-LLB: Dhanyavaad! Zynd Protocol ke saath jude rehna. 🙏")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "bye"):
            print("JOLLY-LLB: Dhanyavaad! Zynd Protocol ke saath jude rehna. 🙏")
            break

        print("\nJOLLY-LLB: (Thinking...)\n")
        response = ask_agent(user_input)

        print(f"JOLLY-LLB:\n{response['answer']}")
        if response["sources"]:
            print(f"\n📚 Sources consulted: {', '.join(response['sources'])}")
        print("\n" + "─" * 60 + "\n")


if __name__ == "__main__":
    interactive_session()
