import os
import json
from dotenv import load_dotenv
from typing import List

# LangChain specific Google GenAI imports
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Dummy data import
try:
    from data.dummy_data import SCHEMES
except ImportError:
    # Agar import fail ho toh dummy structure backup ke liye
    SCHEMES = []

load_dotenv()

VECTOR_DB_PATH = "./vector_db"

def build_documents(schemes: list) -> List[Document]:
    docs = []
    for scheme in schemes:
        # Complex data ko string mein convert karna
        eligibility_text = json.dumps(scheme.get("eligibility", {}), ensure_ascii=False, indent=2)
        benefits_text = json.dumps(scheme.get("benefits", {}), ensure_ascii=False, indent=2)
        
        content = (
            f"Scheme Name: {scheme.get('name', 'N/A')}\n"
            f"Category: {scheme.get('category', 'N/A')}\n"
            f"Description: {scheme.get('description', 'N/A')}\n"
            f"Eligibility: {eligibility_text}\n"
            f"Benefits: {benefits_text}"
        )
        
        metadata = {"id": scheme.get("id", "0"), "title": scheme.get("name", "N/A")}
        docs.append(Document(page_content=content, metadata=metadata))
    return docs

def run_ingestion():
    print("=" * 60)
    print("  POLICY-NAVIGATOR — Data Ingestion Pipeline (Fixed)")
    print("=" * 60)

    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found in .env file.")
        return

    # Step 1: Build docs
    docs = build_documents(SCHEMES)
    print(f"\n[1/2] Prepared {len(docs)} documents.")

    # Step 2: Setup Embeddings using standard LangChain class
    # Isse gRPC errors nahi aayenge
    print("[2/2] Initializing Embeddings...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Step 3: Build ChromaDB
    print(f"Building Vector Store at '{VECTOR_DB_PATH}'...")
    
    # Purana folder delete karna safe hai fresh start ke liye
    import shutil
    if os.path.exists(VECTOR_DB_PATH):
        shutil.rmtree(VECTOR_DB_PATH)

    vector_db = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=VECTOR_DB_PATH
    )

    print("\n✅ Milestone 1 Complete!")
    print(f"Brain saved to: {os.path.abspath(VECTOR_DB_PATH)}")

if __name__ == "__main__":
    run_ingestion()