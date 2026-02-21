"""Step-by-step pipeline test: embeddings, FAISS retrieval, then Groq LLM."""
import warnings
warnings.filterwarnings("ignore")
import os, time
from dotenv import load_dotenv
load_dotenv()

from google import genai as google_genai
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from typing import List

FAISS_INDEX_PATH = "./faiss_index"

class GeminiEmbeddings(Embeddings):
    def __init__(self, model="models/gemini-embedding-001"):
        self.client = google_genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        self.model = model
    def embed_documents(self, texts):
        result = self.client.models.embed_content(model=self.model, contents=texts)
        return [e.values for e in result.embeddings]
    def embed_query(self, text):
        result = self.client.models.embed_content(model=self.model, contents=[text])
        return result.embeddings[0].values

question = "I am a minority student in Class 9 and my family income is 80,000 rupees per year. Am I eligible for any scholarship?"

print("=" * 60)
print("  JOLLY-LLB — Full Pipeline Test")
print("=" * 60)

# Step 1: Embeddings
print("\n[1/3] Testing Google embedding model...")
emb = GeminiEmbeddings()
vec = emb.embed_query("test")
print(f"   Embedding OK — vector dim: {len(vec)}")

# Step 2: FAISS Retrieval
print("\n[2/3] Retrieving relevant schemes from FAISS...")
db = FAISS.load_local(FAISS_INDEX_PATH, emb, allow_dangerous_deserialization=True)
docs = db.similarity_search(question, k=3)
print(f"   Retrieved {len(docs)} scheme(s):")
for d in docs:
    print(f"     • {d.metadata.get('title')}")
context = "\n\n".join(d.page_content[:400] for d in docs)

# Step 3: Groq LLM
print("\n[3/3] Calling Groq LLM (llama-3.3-70b-versatile)...")
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    api_key=os.environ.get("GROQ_API_KEY"),
)
prompt = f"""You are JOLLY-LLB, a Citizen Advocate AI powered by the Zynd Protocol.
Use the context below to answer the citizen's question.
List eligibility criteria, benefits, and numbered next steps with the portal URL.
End with: "Verified by JOLLY-LLB via Zynd Protocol."

Context:
{context}

Question: {question}

Response:"""

response = llm.invoke([HumanMessage(content=prompt)])
print(f"   Groq LLM responded!\n")
print("─" * 60)
print(f"Question: {question}\n")
print("JOLLY-LLB Answer:")
print("─" * 60)
print(response.content)
print("=" * 60)
print("  PIPELINE TEST PASSED — All 3 components working!")
print("=" * 60)
