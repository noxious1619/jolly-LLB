import streamlit as st
import os
import json
import time
import requests
from dotenv import load_dotenv

# Import our logic
from scripts.query_agent import ask_agent_with_eligibility

load_dotenv()

# --- CONFIG ---
st.set_page_config(
    page_title="JOLLY-LLB | Citizen Advocate",
    page_icon="🇮🇳",
    layout="wide",
)

# --- STYLING ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0a192f;
        color: #e6f1ff;
    }
    
    /* Header Styling */
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #64ffda;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #8892b0;
        margin-bottom: 2rem;
    }
    
    /* Custom Sidebar Card */
    [data-testid="stSidebar"] {
        background-color: #0d1b2a;
    }

    .sidebar-card {
        background: #1b263b;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #ff9933;
        color: white;
        margin-bottom: 1rem;
    }
    
    /* Architecture Stepper */
    .step-box {
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 10px;
        transition: all 0.3s;
    }
    
    .step-pending { background: #1b263b; color: #586e75; border: 1px dashed #586e75; }
    .step-active { 
        background: #172a45; 
        color: #64ffda; 
        border: 1px solid #64ffda; 
        font-weight: 600;
        box-shadow: 0 0 10px rgba(100, 255, 218, 0.2);
    }
    .step-done { background: #112240; color: #a5d6a7; border: 1px solid #a5d6a7; }
    
    /* Chat bubbles */
    .user-bubble {
        background: #112240;
        color: #ccd6f6;
        padding: 1rem;
        border-radius: 15px 15px 0 15px;
        margin: 10px 0;
        border: 1px solid #233554;
    }
    
    .agent-bubble {
        background: #172a45;
        color: #e6f1ff;
        padding: 1rem;
        border-radius: 15px 15px 15px 0;
        border: 1px solid #233554;
        margin: 10px 0;
    }

    /* Apply Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #003366;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = {
        "full_name": "Sagar Bhai",
        "age": 25,
        "income": 80000,
        "community": "OBC",
        "is_farmer": True,
        "occupation": "Farmer",
        "state": "Uttar Pradesh",
        "is_rural": True,
        "is_minority": False,
        "aadhaar": "123456789012",
        "mobile": "9876543210"
    }

# --- SIDEBAR: PROFILE ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=80)
    st.markdown("<h2 style='color:#003366; margin-top:0;'>Citizen Profile</h2>", unsafe_allow_html=True)
    
    with st.expander("📝 Edit Demographic Details", expanded=False):
        p = st.session_state.profile
        p["full_name"] = st.text_input("Full Name", p["full_name"])
        p["age"] = st.number_input("Age", value=p["age"], step=1)
        p["income"] = st.number_input("Annual Income (₹)", value=p["income"], step=5000)
        p["community"] = st.selectbox("Category", ["General", "OBC", "SC", "ST", "Minority"], index=["General", "OBC", "SC", "ST", "Minority"].index(p["community"]))
        p["occupation"] = st.text_input("Occupation", p["occupation"])
        p["state"] = st.text_input("State", p["state"])
        
    with st.expander("🚜 Assets & Status", expanded=True):
        p["is_farmer"] = st.checkbox("Is Farmer?", p["is_farmer"])
        p["is_rural"] = st.checkbox("Resides in Rural area?", p["is_rural"])
        p["is_minority"] = st.checkbox("Belongs to Minority Group?", p["is_minority"])

    st.markdown("---")
    st.markdown("<h3 style='color:#003366;'>Architecture Status</h3>", unsafe_allow_html=True)
    
    # Stepper logic
    steps = [
        {"id": "search", "label": "Semantic Search (FAISS)"},
        {"id": "eligible", "label": "Eligibility Gate (Deterministic)"},
        {"id": "llm", "label": "RAG Reasoning (Groq)"},
        {"id": "zynd", "label": "Zynd Trust Verification"}
    ]
    
    # Placeholder for status indicator (we'll update this in the query loop)
    status_placeholders = {s["id"]: st.empty() for s in steps}
    
    for s in steps:
        status_placeholders[s["id"]].markdown(f"<div class='step-box step-pending'>⚪ {s['label']}</div>", unsafe_allow_html=True)

# --- MAIN UI ---
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("<br>", unsafe_allow_html=True)
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=120)
with col2:
    st.markdown("<div class='main-header'>JOLLY-LLB</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Verified Citizen Advocate Agent | Zynd Protocol | Aickathon 2026</div>", unsafe_allow_html=True)

st.markdown("---")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask about any government scheme (e.g., 'Am I eligible for PM-KISAN?')"):
    # Clear steps at start
    for s_id in status_placeholders:
        status_placeholders[s_id].markdown(f"<div class='step-box step-pending'>⚪ {steps[[x['id'] for x in steps].index(s_id)]['label']}</div>", unsafe_allow_html=True)

    # 1. User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Agent Processing
    with st.chat_message("assistant"):
        msg_placeholder = st.empty()
        msg_placeholder.info("Analyzing your request...")

        # --- STEP 1: SEARCH ---
        status_placeholders["search"].markdown("<div class='step-box step-active'>🔍 Searching Knowledge Base...</div>", unsafe_allow_html=True)
        time.sleep(0.5) # for visual effect
        
        # Determine target policy (simple detection for demo, real uses LLM)
        target_policy_id = "scheme_001" # fallback
        if "kisan" in prompt.lower() or "farmer" in prompt.lower():
            target_policy_id = "scheme_002"
        elif "seed" in prompt.lower() or "startup" in prompt.lower():
            target_policy_id = "scheme_003"
        elif "scholarship" in prompt.lower():
            target_policy_id = "scheme_001"

        status_placeholders["search"].markdown("<div class='step-box step-done'>✅ Semantic Search Complete</div>", unsafe_allow_html=True)

        # --- STEP 2: ELIGIBILITY ---
        status_placeholders["eligible"].markdown("<div class='step-box step-active'>🛡️ Verifying Rules...</div>", unsafe_allow_html=True)
        time.sleep(0.4)
        
        # --- STEP 3: LLM REASONING ---
        status_placeholders["llm"].markdown("<div class='step-box step-active'>🧠 Generating Advocate Response...</div>", unsafe_allow_html=True)
        
        try:
            result = ask_agent_with_eligibility(
                user_profile=st.session_state.profile,
                target_policy_id=target_policy_id,
                user_query=prompt
            )
            
            full_response = result["answer"]
            if not full_response: # case where status == failed
                full_response = result["nba_message"]

            status_placeholders["eligible"].markdown(f"<div class='step-box step-done'>✅ Status: {result['nba_status'].upper()}</div>", unsafe_allow_html=True)
            status_placeholders["llm"].markdown("<div class='step-box step-done'>✅ Response Synthesized</div>", unsafe_allow_html=True)

            # --- STEP 4: ZYND TRUST ---
            status_placeholders["zynd"].markdown("<div class='step-box step-active'>🔒 Signing with Zynd Protocol...</div>", unsafe_allow_html=True)
            time.sleep(0.3)
            status_placeholders["zynd"].markdown("<div class='step-box step-done'>✅ Verified via did:zynd:...</div>", unsafe_allow_html=True)

            msg_placeholder.markdown(full_response)
            
            # Show sources if any
            if result.get("sources"):
                st.caption(f"📚 Sources: {', '.join(result['sources'])}")

            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # --- ACTION PANEL ---
            if result["nba_status"] in ("success", "redirect"):
                st.markdown("### ⚡ Quick Actions")
                col_a, col_b = st.columns(2)
                
                with col_a:
                    sid = result["alternative"]["scheme_id"] if result["nba_status"] == "redirect" else target_policy_id
                    
                    if st.button("🚀 Start Auto-Fill Process", key="start_fill"):
                        st.session_state.filling_active = True
                        st.session_state.target_sid = sid
                    
                    if st.session_state.get("filling_active"):
                        st.info(f"Initiating Agent for: {st.session_state.target_sid}")
                        try:
                            # 1. Start the form (if not already started)
                            if not st.session_state.get("form_started"):
                                response = requests.post(
                                    "http://localhost:8000/start-form",
                                    json={
                                        "scheme_id": st.session_state.target_sid,
                                        "user_data": st.session_state.profile
                                    }
                                )
                                if response.status_code == 200:
                                    st.session_state.form_started = True
                                    st.success("Browser launched! Please switch to the portal window and log in.")
                                else:
                                    st.error(f"Error: {response.json().get('detail')}")
                        
                            # 2. Resume button (visible once started)
                            if st.session_state.get("form_started"):
                                st.write("👇 Once you see the form page, click below:")
                                if st.button("✅ I'm Ready - Fill Form Now!", type="primary"):
                                    res = requests.post("http://localhost:8000/resume-form")
                                    if res.status_code == 200:
                                        st.success("Filling started! 🚜 View the browser window.")
                                        st.session_state.filling_active = False
                                        st.session_state.form_started = False
                                    else:
                                        st.error(f"Resume failed: {res.json().get('detail')}")
                        
                        except Exception as e:
                            st.error(f"Backend offline: {e}. Run `uvicorn api.server:app` first.")

                with col_b:
                    if st.button("📄 Generate PDF Checklist"):
                        st.toast("Feature coming soon: PDF checklist generation.")

        except Exception as e:
            st.error(f"Advocate Error: {e}")
            msg_placeholder.error("I encountered an issue while processing the policies.")

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.caption("© 2026 JOLLY-LLB | Built for Zynd Protocol Aickathon")
