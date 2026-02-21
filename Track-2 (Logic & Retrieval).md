Python

with open("Hackathon Feature Implementation Plan.md", "r") as f:  
    print(f.read())

Code output  
This is an excellent way to structure the hackathon workflow. By completely decoupling the conversational experience from the deterministic logic, Garv and your other teammate can build and test their systems independently using mock data until it is time to integrate.

Here is the detailed implementation plan, broken down into phases and milestones for both tracks.

\#\#\# \---

\*\*Track 1: The Conversational & Extraction Layer\*\*

\*\*Assignee:\*\* Garv

\*\*Focus:\*\* LLM orchestration, semantic routing, and structured JSON extraction.

\#\#\#\# \*\*Phase 1: Foundation (Semantic Routing & Chatbot)\*\*

The first goal is to ensure the agent understands what the user is trying to do before blindly searching the database.

| Milestone | Task | Description |  
| :---- | :---- | :---- |  
| \*\*1.1\*\* | \*\*Semantic Router\*\* | Implement a lightweight classification layer at the entry point. This decides if the user's prompt is a casual greeting/general query or a specific intent to search for policies. |  
| \*\*1.2\*\* | \*\*Fallback Conversation\*\* | Route non-policy intents to a standard LangChain ConversationChain. Equip this chain with conversation memory so the bot can maintain a natural dialogue without triggering the heavy retrieval pipeline. |

\#\#\#\# \*\*Phase 2: Information Extraction (RAG Setup & Missing Info)\*\*

Once the user is securely routed into the policy flow, the system must extract data reliably.

| Milestone | Task | Description |  
| :---- | :---- | :---- |  
| \*\*2.1\*\* | \*\*Pydantic Schemas\*\* | Define the required variables for each scheme (e.g., age, income, state, aadhar\\\_status) using strict Pydantic data models. |  
| \*\*2.2\*\* | \*\*Structured Output\*\* | Configure the LangChain pipeline to force the Groq LLM to populate the schema. Use JsonOutputParser to ensure the model responds strictly with a parseable JSON object representing the user's profile. |  
| \*\*2.3\*\* | \*\*Conversational Loop\*\* | Write a dictionary evaluation script. If the parsed JSON returns a null value for a critical key, the script pauses the flow and triggers a secondary prompt asking the user to provide that specific missing detail. |

Based on the document you shared, **Track-2 (The Logic & Retrieval Layer)** is the most critical part of your backend architecture. It acts as the "brain" and the "guardrail" of your system. It ensures that the LLM does not hallucinate eligibility and smartly finds alternatives if a user is rejected.

Here is the detailed implementation plan, breaking down the steps, rules, minimal code, and testing strategies for Track-2.

---

### **Phase 1: Core Logic (Deterministic Engine)**

**Goal:** Strip the decision-making power away from the LLM. You will use strict, hardcoded Python logic to check if the user's JSON profile matches the policy's requirements.

#### **Steps & Rules**

1. **Rule 1: Standardized Data Structuring:** All your policies must be stored in a strict machine-readable format (like Python dictionaries or JSON).  
2. **Rule 2: Absolute Boolean Output:** The LLM should never guess. Your Python engine must output a strict True or False based on pure math (e.g., user\_income \<= policy\_limit).  
3. **Step 1:** Create a database/dictionary of policies.  
4. **Step 2:** Write the deterministic if/elif/else engine that acts as the final gatekeeper.

#### **Minimal Code Implementation**

Python

\# 1\. Policy Data Structuring (Mock Database)  
policy\_db \= {  
    "pm\_kisan": {"min\_age": 18, "max\_income\_inr": 200000},  
    "startup\_india": {"min\_age": 18, "max\_income\_inr": 1000000}  
}

\# 2\. Boolean Engine & Guardrail  
def verify\_eligibility(user\_profile: dict, policy\_id: str) \-\> tuple\[bool, str\]:  
    policy \= policy\_db.get(policy\_id)  
    if not policy:  
        return False, "Policy not found."  
      
    \# Strict deterministic math (No LLM involved)  
    if user\_profile.get("age", 0) \< policy\["min\_age"\]:  
        return False, "Age is below the minimum requirement."  
          
    if user\_profile.get("income", float('inf')) \> policy\["max\_income\_inr"\]:  
        return False, "Income exceeds the maximum allowed limit."  
          
    return True, "Eligible"

#### **Testing Strategy (Phase 1\)**

* **Unit Testing:** Create mock JSON objects for different user scenarios.  
* **Pass Case:** user \= {"age": 25, "income": 50000}. Assert that calling verify\_eligibility(user, "pm\_kisan") returns True.  
* **Fail Case:** user \= {"age": 16, "income": 50000}. Assert that it returns False and catches the exact reason ("Age is below...").

---

### **Phase 2: Advanced Retrieval (Next Best Action)**

**Goal:** If Phase 1 returns False, you do not want to leave the user empty-handed. You need to intercept that failure and automatically query your Vector DB (ChromaDB) to find a policy they *actually* qualify for.

#### **Steps & Rules**

1. **Rule 1: Intercept the Flag:** Your backend must catch the False flag from Phase 1 and prevent the system from sending a simple "No" to the user.  
2. **Rule 2: Metadata is Mandatory:** When you upload documents to ChromaDB, you *must* attach numerical limits as metadata. Without metadata, you cannot filter accurately.  
3. **Step 1:** Extract the user's exact constraints (e.g., their income is exactly 300,000).  
4. **Step 2:** Trigger a silent backend query to ChromaDB using **Metadata Filtering** (e.g., $gte \- greater than or equal to) to find policies where the income limit accommodates the user.

#### **Minimal Code Implementation**

Python

\# Assuming 'collection' is your initialized ChromaDB collection

def handle\_policy\_request(user\_profile: dict, target\_policy\_id: str):  
    \# 1\. Run the Guardrail  
    is\_eligible, reason \= verify\_eligibility(user\_profile, target\_policy\_id)  
      
    if is\_eligible:  
        return {"status": "success", "message": "You are eligible\! Let's apply."}  
      
    \# 2\. Intercept Logic & Dynamic Re-Querying  
    print(f"Rejected: {reason}. Triggering Next Best Action...")  
      
    \# 3\. Metadata Filtering in ChromaDB  
    \# We want policies where the 'max\_income' allowed is Greater Than or Equal ($gte) to the user's income  
    results \= collection.query(  
        query\_texts=\["financial assistance scheme"\],  
        n\_results=1,  
        where={  
            "max\_income\_inr": {"$gte": user\_profile.get("income", 0)}  
        }  
    )  
      
    \# Extract the alternative scheme name  
    if results\['metadatas'\] and len(results\['metadatas'\]\[0\]) \> 0:  
        alternative\_scheme \= results\['metadatas'\]\[0\]\[0\].get('scheme\_name')  
        return {"status": "redirect", "message": f"You are not eligible for {target\_policy\_id}, but based on your profile, you can apply for {alternative\_scheme}."}  
      
    return {"status": "failed", "message": "No suitable policies found."}

#### **Testing Strategy (Phase 2\)**

* **Mock ChromaDB:** Populate a local ChromaDB collection with 3 dummy schemes, ensuring you add metadata like {"max\_income\_inr": 500000, "scheme\_name": "State Subsidy"}.  
* **Integration Test:** Pass a user\_profile that has an income of 300,000 and wants to apply for "pm\_kisan" (limit 200,000).  
* **Assertion:** Verify that the system successfully rejects "pm\_kisan", silently hits ChromaDB, and returns "State Subsidy" as the fallback option.

