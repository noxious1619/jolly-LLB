import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

def ask_policy_agent(user_query):
    # 1. Load the saved memory
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_db = Chroma(persist_directory="./vector_db", embedding_function=embeddings)

    # 2. Setup Gemini AI Model
    # 'gemini-1.5-flash' hackathons ke liye best hai kyunki ye bahut fast hai
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

    # 3. Create QA Chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vector_db.as_retriever()
    )

    # 4. Get Answer
    response = qa_chain.invoke(user_query)
    return response["result"]

if __name__ == "__main__":
    query = "Is policy ke hisaab se eligibility criteria kya hain? Aasaan bhasha mein samjhao."
    print("\n--- Agent Answer ---\n")
    print(ask_policy_agent(query))