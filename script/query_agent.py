import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

load_dotenv()

def ask_agent(user_query):
    # 1. Load the existing Vector DB
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_db = Chroma(persist_directory="./vector_db", embedding_function=embeddings)

    # 2. Setup Gemini Model (Flash is great for speed)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.2)

  
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_db.as_retriever(search_kwargs={"k": 2})
    )

    # 4. Generate Response
    response = qa_chain.invoke(user_query)
    return response["result"]

if __name__ == "__main__":
    # Test Question
    test_q = "Main ek girl student hoon aur meri family income 1 lakh hai. Kya mujhe help milegi?"
    print("\n--- Testing Agent ---\n")
    print(f"User: {test_q}")
    print(f"Agent: {ask_agent(test_q)}")