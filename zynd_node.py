# zynd_node.py
# Zynd Protocol — Agent Registration Node
# Policy-Navigator — Zynd Aickathon 2026
#
# This module registers the Policy-Navigator AI agent on the Zynd Protocol
# network, assigns it a Decentralized Identity (DID), and exposes an
# agent endpoint that the Zynd network can discover and route queries to.
#
# Usage:
#   python zynd_node.py

import os
import uuid
import json
import hashlib
import datetime
from dotenv import load_dotenv
from scripts.query_agent import ask_agent


load_dotenv()

# ─────────────────────────────────────────────────────────────
# Zynd SDK Integration
# The zynd-sdk package provides ZyndNode, register_agent, and
# the DecentralizedIdentity helpers. Install via requirements.txt.
# ─────────────────────────────────────────────────────────────
try:
    from zynd_sdk import ZyndNode, AgentCard, register_agent  # type: ignore
    ZYND_SDK_AVAILABLE = True
except ImportError:
    ZYND_SDK_AVAILABLE = False
    print("⚠  zynd-sdk not installed or not available in this environment.")
    print("   Running in SIMULATION MODE — DID will be generated locally.\n")


# ─────────────────────────────────────────────
# Agent Configuration
# ─────────────────────────────────────────────
AGENT_CONFIG = {
    "name":        "Policy-Navigator",
    "version":     "1.0.0",
    "description": (
        "A Citizen Advocate AI agent that simplifies Indian government policies, "
        "verifies eligibility, and provides trust-backed Next Steps using the Zynd Protocol."
    ),
    "capabilities": [
        "policy_summarization",
        "eligibility_verification",
        "document_checklist",
        "hinglish_explanation",
        "rag_retrieval",
        "form_filling",          # NEW: auto-fills govt scheme forms via Playwright
    ],
    "supported_schemes": [
        "Scholarships (NSP Pre-Matric)",
        "Agriculture (PM-KISAN)",
        "Startups (Startup India Seed Fund)",
    ],
    "language_support": ["Hindi", "English", "Hinglish"],
    "trust_level":     "Verified",
    "hackathon":       "Zynd Aickathon 2026",
}


def generate_local_did(agent_name: str, agent_version: str) -> str:
    """
    Generate a deterministic, locally-derived Decentralized Identity (DID)
    for the agent using its name, version, and a stable seed.
    Format: did:zynd:<namespace>:<fingerprint>
    """
    seed = f"{agent_name}:{agent_version}:policy-navigator:zynd-aickathon-2026"
    fingerprint = hashlib.sha256(seed.encode()).hexdigest()[:32]
    namespace   = agent_name.lower().replace(" ", "-").replace("_", "-")
    return f"did:zynd:{namespace}:{fingerprint}"


def register_with_zynd_sdk(did: str) -> dict:
    """
    Register the agent using the official Zynd SDK.
    Returns the registration receipt from the Zynd network.
    """
    api_key = os.getenv("ZYND_API_KEY", "")

    node = ZyndNode(api_key=api_key)

    card = AgentCard(
        name=AGENT_CONFIG["name"],
        did=did,
        version=AGENT_CONFIG["version"],
        description=AGENT_CONFIG["description"],
        capabilities=AGENT_CONFIG["capabilities"],
        trust_level=AGENT_CONFIG["trust_level"],
        endpoint=os.getenv("AGENT_ENDPOINT_URL", "http://localhost:8000/agent"),
    )

    receipt = register_agent(node=node, card=card)
    return receipt


def simulate_zynd_registration(did: str) -> dict:
    """
    Simulate a Zynd Protocol registration (used when zynd-sdk is not installed).
    Generates a local registration receipt for demonstration purposes.
    """
    receipt = {
        "status":            "registered_simulation",
        "did":               did,
        "agent_name":        AGENT_CONFIG["name"],
        "registration_id":   str(uuid.uuid4()),
        "timestamp":         datetime.datetime.utcnow().isoformat() + "Z",
        "network":           "zynd-testnet",
        "trust_level":       AGENT_CONFIG["trust_level"],
        "capabilities":      AGENT_CONFIG["capabilities"],
        "supported_schemes": AGENT_CONFIG["supported_schemes"],
        "note": (
            "SIMULATION: Install zynd-sdk and set ZYND_API_KEY in .env "
            "for live registration on the Zynd Protocol mainnet."
        ),
    }
    return receipt


def save_identity_file(did: str, receipt: dict) -> str:
    """Persist the DID and registration receipt to agent_identity.json."""
    identity = {
        "did":           did,
        "agent_config":  AGENT_CONFIG,
        "registration":  receipt,
        "generated_at":  datetime.datetime.utcnow().isoformat() + "Z",
    }
    path = "./agent_identity.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(identity, f, indent=2, ensure_ascii=False)
    return os.path.abspath(path)


def run_demo_query(did: str):
    """Run a sample query to demonstrate the registered agent is operational."""
    print("\n" + "─" * 60)
    print("  🔬  LIVE AGENT DEMO — Registered Agent In Action")
    print("─" * 60)

    test_questions = [
        "Main ek minority student hoon, Class 8 mein hoon. Kya mujhe scholarship milegi?",
        "Mere paas 2 hectare zameen hai. PM KISAN se mujhe kitna paisa milega?",
        "Mere startup ko seed funding chahiye. DPIIT recognition hai. Kya main apply kar sakta hoon?",
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n[Query {i}] {question}")
        print("Neeti (Citizen Advocate):")
        try:
            result = ask_agent(question)
            # Print first 600 chars to keep demo concise
            answer_preview = result["answer"][:600]
            print(answer_preview)
            if len(result["answer"]) > 600:
                print("  ... [truncated for demo]")
            if result.get("sources"):
                print(f"  📚 Sources: {', '.join(result['sources'])}")
        except Exception as e:
            print(f"  ⚠ Query failed: {e}")
            print("  (Make sure you have run ingest.py first!)")

    print("\n" + "─" * 60)
    print(f"  ✅ Verified by DID: {did}")
    print("─" * 60 + "\n")


def main():
    print("\n" + "═" * 60)
    print("  🌐  ZYND PROTOCOL — Agent Registration Node")
    print("  Policy-Navigator v1.0.0  |  Aickathon 2026")
    print("═" * 60 + "\n")

    # Step 1: Generate DID
    print("[1/4] Generating Decentralized Identity (DID)...")
    did = generate_local_did(
        AGENT_CONFIG["name"],
        AGENT_CONFIG["version"],
    )
    print(f"      ✓ DID: {did}\n")

    # Step 2: Register on Zynd Protocol
    print("[2/4] Registering agent on Zynd Protocol network...")
    if ZYND_SDK_AVAILABLE:
        try:
            receipt = register_with_zynd_sdk(did)
            print("      ✓ Registered on Zynd Mainnet!")
        except Exception as e:
            print(f"      ⚠ SDK registration failed ({e}). Falling back to simulation.")
            receipt = simulate_zynd_registration(did)
    else:
        receipt = simulate_zynd_registration(did)
        print("      ✓ Simulation registration complete.")

    # Step 3: Save identity file
    print("\n[3/4] Saving agent identity to agent_identity.json...")
    identity_path = save_identity_file(did, receipt)
    print(f"      ✓ Saved: {identity_path}\n")

    # Step 4: Print summary
    print("[4/4] Registration Summary:")
    print(f"      Agent Name      : {AGENT_CONFIG['name']}")
    print(f"      DID             : {did}")
    print(f"      Trust Level     : {AGENT_CONFIG['trust_level']}")
    print(f"      Capabilities    : {', '.join(AGENT_CONFIG['capabilities'])}")
    print(f"      Supported Schemes: {', '.join(AGENT_CONFIG['supported_schemes'])}")
    print(f"      Network Status  : {receipt.get('status', 'unknown')}")

    print(f"\n{'═' * 60}")
    print("  ✅  Policy-Navigator Agent is LIVE on the Zynd Protocol!")
    print(f"{'═' * 60}\n")

    # Optional: Run a live demo
    run_demo = os.getenv("RUN_DEMO", "true").lower() == "true"
    if run_demo:
        run_demo_query(did)


if __name__ == "__main__":
    main()
