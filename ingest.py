import os
import json
from dotenv import load_dotenv
from typing import List

# Stable Imports
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Dummy data import
try:
    from data.dummy_data import SCHEMES
except ImportError:
    SCHEMES = [{"id": 1, "name": "Test", "description": "Test", "eligibility": {}}]

load_dotenv()

def build_documents(schemes: list) -> List[Document]:
    docs = []
    for scheme in schemes:
        eligibility = json.dumps(scheme.get("eligibility", {}), ensure_ascii=False, indent=2)
        content = f"Scheme: {scheme.get('name')}\nDescription: {scheme.get('description')}\nEligibility: {eligibility}"
        docs.append(Document(page_content=content, metadata={"title": scheme.get("name")}))
    return docs

def run_ingestion():
    print("=" * 60)
    print("🚀 POLICY NAVIGATOR — Milestone 1 (Auto-Model Mode)")
    print("=" * 60)
    
    # Try different model name variations that Google accepts
    model_names = ["text-embedding-004", "models/text-embedding-004", "embedding-001"]
    
    success = False
    for model_name in model_names:
        print(f"Trying with model: {model_name}...")
        try:
            embeddings = GoogleGenerativeAIEmbeddings(
                model=model_name,
                transport="rest"
            )
            
            docs = build_documents(SCHEMES)
            vector_db = FAISS.from_documents(docs, embeddings)
            
            # Save the index locally
            vector_db.save_local("faiss_index")
            
            print(f"\n✅ Milestone 1 Complete with model: {model_name}!")
            print("Brain (FAISS Index) saved to 'faiss_index' folder.")
            success = True
            break
        except Exception as e:
            print(f"❌ Failed with {model_name}: {e}")
            continue

    if not success:
        print("\n🆘 All models failed. Please check if your API Key is valid and has 'Generative AI API' enabled in Google Cloud/AI Studio.")

if __name__ == "__main__":
    run_ingestion()