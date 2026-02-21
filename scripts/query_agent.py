import os
from typing import List, Optional
from dotenv import load_dotenv

from google import genai as google_genai
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.embeddings import Embeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from logic.next_best_action import handle_policy_request

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
    input_variables=["context", "question", "profile"],
    template="""You are JOLLY-LLB, a trusted Citizen Advocate AI powered by the Zynd Protocol.
Your mission is to make Indian government policies simple, accessible, and actionable for every citizen.

## Your Responsibilities:
1. **Policy Summary:** Explain the policy clearly and simply.
2. **Eligibility Check:** Clearly state who qualifies and who does NOT based on the Citizen Profile below.
3. **Avoid Redundancy:** DO NOT ask for information already present in the Citizen Profile.
4. **Next Steps:** Provide numbered application steps with the official portal URL.
5. **Trust Signal:** End with: "Verified by JOLLY-LLB via Zynd Protocol."

## Citizen Profile (Sidebar Data):
{profile}

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
        {
            "context": (lambda x: x["question"]) | retriever | format_docs,
            "question": lambda x: x["question"],
            "profile": lambda x: x["profile"]
        }
        | CITIZEN_ADVOCATE_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain, retriever


def ask_agent(user_query: str) -> dict:
    """Return the agent's answer and source schemes used (RAG-only, no eligibility gate)."""
    vector_db = load_vector_db()
    chain, retriever = build_qa_chain(vector_db)

    answer = chain.invoke({"question": user_query, "profile": "N/A (CLI Session)"})
    source_docs = retriever.invoke(user_query)
    sources = list({doc.metadata.get("title", "Unknown") for doc in source_docs})

    return {"answer": answer, "sources": sources}


def ask_agent_with_eligibility(
    user_profile: dict,
    target_policy_id: str,
    user_query: str,
) -> dict:
    """
    Track-2 — Full eligibility-gated agent call.

    Flow
    ----
    1. Load FAISS index.
    2. Run Next Best Action (deterministic eligibility gate + optional redirect).
    3a. If eligible   → run RAG chain normally; LLM elaborates on the scheme.
    3b. If redirected → prepend NBA redirect notice to the question so the LLM
                        focuses its response on the alternative scheme.
    3c. If no scheme  → return the NBA failure message directly.

    Parameters
    ----------
    user_profile      : dict with user's demographic/financial details
                        e.g. {"age": 25, "income": 80000, "community": "Muslim"}
    target_policy_id  : scheme id to check first, e.g. "scheme_001"
    user_query        : the citizen's free-text question for the LLM

    Returns
    -------
    {
      "nba_status":  "success" | "redirect" | "failed",
      "nba_message": <NBA verdict string>,
      "answer":      <LLM response string, or empty on failed>,
      "sources":     [list of scheme titles used],
      "alternative": <alternative scheme dict or None>,
    }
    """
    vector_db = load_vector_db()

    # ── Track-2 Gate ──────────────────────────────────────────────────────────
    nba_result = handle_policy_request(
        user_profile=user_profile,
        target_policy_id=target_policy_id,
        faiss_db=vector_db,
    )

    status = nba_result["status"]

    # ── No viable scheme — skip LLM ───────────────────────────────────────────
    if status == "failed":
        return {
            "nba_status": "failed",
            "nba_message": nba_result["message"],
            "answer": "",
            "sources": [],
            "alternative": None,
        }

    # ── Build the RAG chain ───────────────────────────────────────────────────
    chain, retriever = build_qa_chain(vector_db)

    if status == "redirect":
        # Steer the LLM toward the alternative scheme
        alt = nba_result["alternative"]
        enriched_query = (
            f"{nba_result['message']}\n\n"
            f"Please elaborate on the alternative scheme "
            f"'{alt['name']}' and provide eligibility details and next steps. "
            f"Original citizen question: {user_query}"
        )
    else:
        # Directly eligible — answer the original question
        enriched_query = user_query

    # Inject profile into the chain
    answer = chain.invoke({"question": enriched_query, "profile": str(user_profile)})
    source_docs = retriever.invoke(enriched_query)
    sources = list({doc.metadata.get("title", "Unknown") for doc in source_docs})

    return {
        "nba_status": status,
        "nba_message": nba_result["message"],
        "answer": answer,
        "sources": sources,
        "alternative": nba_result.get("alternative"),
    }


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