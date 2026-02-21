import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

def setup_knowledge_base():
    # 1. Load PDF (Make sure 'data' folder has your PDF)
    file_path = "data/policy.pdf" # Apni file ka naam yahan check karein
    loader = PyPDFLoader(file_path)
    data = loader.load()

    # 2. Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(data)

    # 3. Create Vector Store with Gemini Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_db = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings,
        persist_directory="./vector_db"
    )
    print(f"Memory saved successfully! Total chunks: {len(chunks)}")

if __name__ == "__main__":
    setup_knowledge_base()