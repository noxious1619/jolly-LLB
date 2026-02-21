import os
from typing import List
from dotenv import load_dotenv

from google import genai as google_genai
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.embeddings import Embeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

FAISS_INDEX_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "faiss_index")


class GeminiEmbeddings(Embeddings):
    """Google embeddings for semantic search (Groq has no embedding API)."""

    def __init__(self, model: str = "models/gemini-embedding-001"):
        self.client = google_genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        result = self.client.models.embed_content(model=self.model, contents=texts)
        return [e.values for e in result.embeddings]

    def embed_query(self, text: str) -> List[float]:
        result = self.client.models.embed_content(model=self.model, contents=[text])
        return result.embeddings[0].values


CITIZEN_ADVOCATE_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are JOLLY-LLB, a trusted Citizen Advocate AI powered by the Zynd Protocol.
Your mission is to make Indian government policies simple, accessible, and actionable for every citizen.

## Your Responsibilities:
1. **Policy Summary:** Explain the policy clearly and simply.
2. **Eligibility Check:** Clearly state who qualifies and who does NOT, listing all conditions.
3. **Ask Missing Details:** If income, age, category, or land holding are not mentioned, ask politely.
4. **Next Steps:** Provide numbered application steps with the official portal URL.
5. **Trust Signal:** End with: "Verified by JOLLY-LLB via Zynd Protocol."

Use emojis: 📋 eligibility, 💰 benefits, 📝 steps, ❓ questions.

## Context from Knowledge Base:
{context}

## Citizen Question:
{question}

## JOLLY-LLB Response:
""",
)


def load_vector_db() -> FAISS:
    """Load the FAISS vector store saved by ingest.py."""
    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError(
            f"FAISS index not found at '{FAISS_INDEX_PATH}'.\n"
            "Run first: python ingest.py"
        )
    embeddings = GeminiEmbeddings()
    return FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )


def build_qa_chain(vector_db: FAISS):
    """Build a RAG chain using Groq LLM + FAISS retriever."""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | CITIZEN_ADVOCATE_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain, retriever


def ask_agent(user_query: str) -> dict:
    """Return the agent's answer and source schemes used."""
    vector_db = load_vector_db()
    chain, retriever = build_qa_chain(vector_db)

    answer = chain.invoke(user_query)
    source_docs = retriever.invoke(user_query)
    sources = list({doc.metadata.get("title", "Unknown") for doc in source_docs})

    return {"answer": answer, "sources": sources}


def interactive_session():
    """Run an interactive CLI session with JOLLY-LLB."""
    print("\n" + "═" * 60)
    print("  🇮🇳  JOLLY-LLB — Citizen Advocate")
    print("  Powered by Zynd Protocol + Groq (Llama 3.3 70B)")
    print("═" * 60)
    print("  Ask about any Indian government scheme.")
    print("  Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nJOLLY-LLB: Thank you! Stay connected with the Zynd Protocol. 🙏")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "bye"):
            print("JOLLY-LLB: Thank you! Stay connected with the Zynd Protocol. 🙏")
            break

        print("\nJOLLY-LLB: (Thinking...)\n")
        try:
            response = ask_agent(user_input)
            print(f"JOLLY-LLB:\n{response['answer']}")
            if response["sources"]:
                print(f"\n📚 Sources: {', '.join(response['sources'])}")
        except FileNotFoundError as e:
            print(f"❌ {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        print("\n" + "─" * 60 + "\n")


if __name__ == "__main__":
    interactive_session()