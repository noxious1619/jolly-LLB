import os
import json
from dotenv import load_dotenv
from typing import List

<<<<<<< HEAD
# New google.genai SDK (replaces deprecated google.generativeai)
=======

>>>>>>> 824ad66cbfc35f6c277c9621b967534500cb8e42
from google import genai
from google.genai import types
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

<<<<<<< HEAD
try:
=======
# ── Data Source Toggle ────────────────────────────────────────────────────────
# Set USE_REAL_DATA = True to download 723 real schemes from HuggingFace (slower, first run ~30MB)
# Set USE_REAL_DATA = False to use the local dummy_data.py (fast, no internet needed)
USE_REAL_DATA = False
MAX_SCHEMES = None   # Only used when USE_REAL_DATA=True; set to e.g. 50 for a quick test

if USE_REAL_DATA:
    try:
        from data.load_schemes import load_real_schemes
        SCHEMES = load_real_schemes(max_schemes=MAX_SCHEMES)
        print(f"✅ Loaded {len(SCHEMES)} real schemes from HuggingFace.")
    except Exception as e:
        print(f"⚠️  HuggingFace load failed ({e}), falling back to dummy data.")
        from data.dummy_data import SCHEMES
else:
>>>>>>> 824ad66cbfc35f6c277c9621b967534500cb8e42
    from data.dummy_data import SCHEMES
    print(f"📋 Using local dummy data: {len(SCHEMES)} schemes.")

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
<<<<<<< HEAD
        print("❌ GOOGLE_API_KEY not found. Create a .env file with your key.")
=======
        print(" GOOGLE_API_KEY not found. Create a .env file with your key.")
>>>>>>> 824ad66cbfc35f6c277c9621b967534500cb8e42
        print("   See .env.example for the template.")
        return

    try:
        embeddings = GeminiEmbeddings(model="models/gemini-embedding-001")
        docs = build_documents(SCHEMES)
<<<<<<< HEAD
        print(f"📄 Ingesting {len(docs)} scheme(s)...")
=======
        total = len(docs)
        print(f"📄 Building FAISS index for {total} scheme(s)... (this may take a few minutes)")
>>>>>>> 824ad66cbfc35f6c277c9621b967534500cb8e42

        vector_db = FAISS.from_documents(documents=docs, embedding=embeddings)
        vector_db.save_local("faiss_index")

        print(f"\n✅ Done! FAISS index saved to 'faiss_index/'")
<<<<<<< HEAD
        print(f"   Schemes ingested:")
        for s in SCHEMES:
            print(f"     • {s['name']}")

    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
=======
        print(f"   Total schemes ingested: {total}")
        # Print first 10 scheme names to keep output readable
        preview = SCHEMES[:10]
        for s in preview:
            print(f"     • {s['name']}")
        if total > 10:
            print(f"     ... and {total - 10} more.")

    except Exception as e:
        print(f" Ingestion failed: {e}")
>>>>>>> 824ad66cbfc35f6c277c9621b967534500cb8e42


if __name__ == "__main__":
    run_ingestion()
