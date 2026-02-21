"""
app.py — Streamlit frontend for JOLLY-LLB
Run: streamlit run app.py

Features:
  - Chat interface powered by Groq (llama-3.3-70b) + FAISS RAG
  - "Apply for Scheme" button → calls /start-form (opens browser)
  - "I've Logged In — Fill Form" button → calls /resume-form (fills form)
  - Live status polling
"""

import streamlit as st
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
API_URL  = "http://localhost:8000"
PAGE_TITLE = "JOLLY-LLB — Citizen Advocate"

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="🏛️",
    layout="centered",
)

st.markdown("""
<style>
  .main { max-width: 760px; }
  .stChatMessage { border-radius: 12px; }

  .scheme-card {
    background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
    border: 1px solid #a5d6a7;
    border-left: 4px solid #2e7d32;
    border-radius: 8px;
    padding: 16px;
    margin: 8px 0;
  }
  .status-pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 8px;
  }
  .status-idle     { background:#e3f2fd; color:#1565c0; }
  .status-open     { background:#fff3e0; color:#e65100; }
  .status-filling  { background:#f3e5f5; color:#6a1b9a; }
  .status-done     { background:#e8f5e9; color:#2e7d32; }
  .status-error    { background:#ffebee; color:#b71c1c; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages"     not in st.session_state: st.session_state.messages     = []
if "user_profile" not in st.session_state: st.session_state.user_profile = {}
if "active_scheme" not in st.session_state: st.session_state.active_scheme = None
if "form_status"  not in st.session_state: st.session_state.form_status  = "idle"

# ── Helper: talk to FastAPI ────────────────────────────────────────────────────
def api_start_form(scheme_id: str, user_data: dict):
    try:
        r = requests.post(
            f"{API_URL}/start-form",
            json={"scheme_id": scheme_id, "user_data": user_data},
            timeout=5,
        )
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}


def api_resume_form():
    try:
        r = requests.post(f"{API_URL}/resume-form", timeout=5)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}


def api_get_status():
    try:
        r = requests.get(f"{API_URL}/status", timeout=3)
        return r.json()
    except Exception:
        return {"status": "idle", "message": "API server not reachable"}


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 🏛️ JOLLY-LLB — Citizen Advocate")
st.markdown(
    "Ask me about **any Indian government scheme** — I'll check your eligibility "
    "and offer to fill the application form automatically.",
    help="Powered by Zynd Protocol + Groq + Google Embeddings"
)
st.divider()

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── User profile sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 👤 Your Profile")
    st.caption("Fill in your details — the bot uses these to check eligibility and pre-fill the form.")
    name      = st.text_input("Full Name",          key="name")
    age       = st.number_input("Age",              min_value=1, max_value=120, value=18, key="age")
    community = st.selectbox("Community",
        ["", "Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Zoroastrian", "SC", "ST", "OBC", "General"],
        key="community")
    income    = st.number_input("Annual Family Income (₹)", min_value=0, value=80000, step=1000, key="income")
    land      = st.number_input("Land Holding (acres)", min_value=0.0, value=0.0, step=0.5, key="land_acres")
    aadhaar   = st.text_input("Aadhaar Number",     key="aadhaar")
    bank      = st.text_input("Bank Account No.",   key="bank_account")
    class_lvl = st.selectbox("Class Level (students)",
        ["", "1","2","3","4","5","6","7","8","9","10"], key="class_level")
    school    = st.text_input("School Name",        key="school")

    if st.button("💾 Save Profile"):
        st.session_state.user_profile = {
            "name": name, "age": age, "community": community,
            "income": income, "land_acres": land,
            "aadhaar": aadhaar, "bank_account": bank,
            "class_level": class_lvl, "school_name": school,
        }
        st.success("Profile saved!")

    st.divider()
    st.markdown("### 🔌 Form Filler Status")
    status_data = api_get_status()
    s = status_data.get("status", "idle")
    color_map = {
        "idle": "status-idle", "browser_open": "status-open",
        "filling": "status-filling", "done": "status-done", "error": "status-error",
    }
    label_map = {
        "idle": "⚪ Idle", "browser_open": "🟠 Browser Open",
        "filling": "🟣 Filling...", "done": "🟢 Done", "error": "🔴 Error",
    }
    css_class = color_map.get(s, "status-idle")
    label_text = label_map.get(s, s)
    st.markdown(
        f'<div class="status-pill {css_class}">{label_text}</div>',
        unsafe_allow_html=True,
    )
    st.caption(status_data.get("message", ""))
    st.session_state.form_status = s


# ── Chat input ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about any government scheme..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call JOLLY-LLB agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                from scripts.query_agent import ask_agent
                result = ask_agent(prompt)
                answer  = result["answer"]
                sources = result.get("sources", [])

                st.markdown(answer)
                if sources:
                    st.caption(f"📚 Sources: {', '.join(sources)}")

                # Detect which scheme was discussed and enable Apply button
                scheme_map = {
                    "scholarship": "scheme_001",
                    "nsp":         "scheme_001",
                    "pm-kisan":    "scheme_002",
                    "kisan":       "scheme_002",
                    "sisfs":       "scheme_003",
                    "startup":     "scheme_003",
                    "seed fund":   "scheme_003",
                }
                detected = None
                lower_answer = answer.lower()
                for keyword, sid in scheme_map.items():
                    if keyword in lower_answer or keyword in prompt.lower():
                        detected = sid
                        break
                if detected:
                    st.session_state.active_scheme = detected

                st.session_state.messages.append({"role": "assistant", "content": answer})

            except FileNotFoundError:
                msg = "❌ FAISS index not found. Please run `python ingest.py` first."
                st.error(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
            except Exception as e:
                msg = f"❌ Error: {e}"
                st.error(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})


# ── Action buttons (shown when a scheme is detected) ──────────────────────────
if st.session_state.active_scheme:
    st.divider()
    scheme_names = {
        "scheme_001": "NSP Pre-Matric Scholarship",
        "scheme_002": "PM-KISAN",
        "scheme_003": "Startup India Seed Fund",
    }
    name_display = scheme_names.get(st.session_state.active_scheme, "Scheme")

    st.markdown(
        f'<div class="scheme-card">'
        f'<b>🎯 Scheme Detected: {name_display}</b><br/>'
        f'<small>JOLLY-LLB can open the portal and fill the application form automatically.</small>'
        f'</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🌐 Apply for Scheme", use_container_width=True, type="primary",
                     disabled=st.session_state.form_status in ("browser_open", "filling")):
            profile = st.session_state.user_profile
            if not profile.get("name"):
                st.warning("⚠️ Please fill in your profile in the sidebar first.")
            else:
                resp = api_start_form(st.session_state.active_scheme, profile)
                st.session_state.form_status = resp.get("status", "error")
                st.info(f"🌐 {resp.get('message', '')}")
                st.rerun()

    with col2:
        if st.button("✅ I've Logged In — Fill Form", use_container_width=True,
                     disabled=st.session_state.form_status != "browser_open"):
            resp = api_resume_form()
            st.session_state.form_status = resp.get("status", "error")
            st.success(f"🤖 {resp.get('message', '')}")
            st.rerun()

    with col3:
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()

    if st.session_state.form_status == "done":
        st.success("🎉 Form submitted successfully by JOLLY-LLB!")
    elif st.session_state.form_status == "error":
        st.error("❌ Something went wrong. Check the API server logs.")
    elif st.session_state.form_status == "browser_open":
        st.info("⏸ Browser is open. Please log into the portal, then click **'I've Logged In — Fill Form'**.")
    elif st.session_state.form_status == "filling":
        st.info("🤖 JOLLY-LLB is filling the form...")
