import os
import json
from dotenv import load_dotenv
from typing import List

# New google.genai SDK (replaces deprecated google.generativeai)
from google import genai
from google.genai import types
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

try:
    from data.dummy_data import SCHEMES
except ImportError:
    SCHEMES = [{"id": 1, "name": "Test", "description": "Test", "eligibility": {}}]

load_dotenv()


class GeminiEmbeddings(Embeddings):
    """LangChain-compatible embeddings via new google.genai SDK."""

    def __init__(self, model: str = "models/gemini-embedding-001"):
        self.client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        result = self.client.models.embed_content(
            model=self.model,
            contents=texts,
        )
        return [e.values for e in result.embeddings]

    def embed_query(self, text: str) -> List[float]:
        result = self.client.models.embed_content(
            model=self.model,
            contents=[text],
        )
        return result.embeddings[0].values


def build_documents(schemes: list) -> List[Document]:
    docs = []
    for scheme in schemes:
        eligibility = json.dumps(scheme.get("eligibility", {}), ensure_ascii=False, indent=2)
        content = (
            f"Scheme: {scheme.get('name')}\n"
            f"Description: {scheme.get('description')}\n"
            f"Eligibility: {eligibility}"
        )
        docs.append(Document(page_content=content, metadata={"title": scheme.get("name")}))
    return docs


def run_ingestion():
    print("=" * 60)
    print("🚀 JOLLY-LLB — Data Ingestion into FAISS")
    print("=" * 60)

    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not found. Create a .env file with your key.")
        print("   See .env.example for the template.")
        return

    try:
        embeddings = GeminiEmbeddings(model="models/gemini-embedding-001")
        docs = build_documents(SCHEMES)
        print(f"📄 Ingesting {len(docs)} scheme(s)...")

        vector_db = FAISS.from_documents(documents=docs, embedding=embeddings)
        vector_db.save_local("faiss_index")

        print(f"\n✅ Done! FAISS index saved to 'faiss_index/'")
        print(f"   Schemes ingested:")
        for s in SCHEMES:
            print(f"     • {s['name']}")

    except Exception as e:
        print(f"❌ Ingestion failed: {e}")


if __name__ == "__main__":
    run_ingestion()
