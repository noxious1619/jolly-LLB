"""
Policy-Navigator Agent — ZyndAI Agent SDK Deployment
Zynd Aickathon 2026

This module deploys the Policy-Navigator agent on the Zynd Protocol using the
ZyndAI Agent SDK (LangChain-based). The agent simplifies Indian government
policies, verifies eligibility, and provides next-best actions—all accessible
via the Zynd network with x402 micropayment support.

Usage:
    python zynd_node.py

Requirements:
    - zyndai_agent (from https://github.com/zynd/agent-sdk)
    - langchain, langchain-openai, langchain-community
    - ZYND_API_KEY in .env
"""

import os
import traceback
from dotenv import load_dotenv
from scripts.query_agent import ask_agent_with_eligibility

# ZyndAI Agent SDK imports (with fallback mock for local testing)
try:
    from zyndai_agent.agent import AgentConfig, ZyndAIAgent
    from zyndai_agent.message import AgentMessage
    ZYND_AVAILABLE = True
except ImportError:
    # Fallback: Create local mock classes for development/testing
    ZYND_AVAILABLE = False
    
    class AgentMessage:
        def __init__(self, message_id, content, topic="agent_query"):
            self.message_id = message_id
            self.content = content
            self.topic = topic
    
    class AgentConfig:
        def __init__(self, name, description, capabilities, webhook_host, webhook_port,
                     registry_url, price, api_key, config_dir):
            self.name = name
            self.description = description
            self.capabilities = capabilities
            self.webhook_host = webhook_host
            self.webhook_port = webhook_port
            self.registry_url = registry_url
            self.price = price
            self.api_key = api_key
            self.config_dir = config_dir
    
    class ZyndAIAgent:
        def __init__(self, agent_config):
            self.agent_config = agent_config
            self.webhook_url = f"http://{agent_config.webhook_host}:{agent_config.webhook_port}"
            self.message_handlers = []
            self.agent = None
        
        def set_langchain_agent(self, agent):
            self.agent = agent
        
        def add_message_handler(self, handler):
            self.message_handlers.append(handler)
        
        def invoke(self, query, chat_history=None):
            """Invoke the LangChain agent with a query."""
            if not self.agent:
                return "Agent not initialized."
            result = self.agent.invoke({
                "input": query,
                "chat_history": chat_history or []
            })
            return result.get("output", str(result))
        
        def set_response(self, message_id, response):
            """Log response (in real Zynd SDK, sends back via network)."""
            print(f"\n[Zynd] Response for {message_id}: {response[:100]}...")

# LangChain imports (for tool-calling agent framework)
from langchain_groq import ChatGroq
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

load_dotenv()


# ═══════════════════════════════════════════════════════════════════════════
# AGENT TOOLS
# ═══════════════════════════════════════════════════════════════════════════

@tool
def check_scheme_eligibility(scheme_id: str, user_profile: dict) -> str:
    """
    Check if a citizen is eligible for a specific government scheme.
    
    Args:
        scheme_id: Scheme identifier (e.g., 'scheme_001', 'scheme_002')
        user_profile: Citizen profile dict with keys like age, income, category, etc.
    
    Returns:
        Eligibility status and reasoning.
    """
    try:
        result = ask_agent_with_eligibility(
            user_profile=user_profile,
            target_policy_id=scheme_id,
            user_query=f"Am I eligible for {scheme_id}?"
        )
        status = result.get("nba_status", "unknown")
        answer = result.get("answer", "No information available.")
        return f"Eligibility Status: {status}\n{answer}"
    except Exception as e:
        return f"Error checking eligibility: {str(e)}"


@tool
def get_scheme_info(scheme_id: str) -> str:
    """
    Get detailed information about a government scheme.
    
    Args:
        scheme_id: Scheme identifier (e.g., 'scheme_001' for NSP scholarship)
    
    Returns:
        Scheme details including eligibility criteria, benefits, and documents.
    """
    scheme_map = {
        "scheme_001": "NSP Pre-Matric Scholarship — For students in classes I–VIII",
        "scheme_002": "PM-KISAN — Direct income support for farmers (₹6000/year)",
        "scheme_003": "Startup India SISFS — Seed funding for startups",
        "scheme_004": "PMJAY (Ayushman Bharat) — Health insurance scheme",
        "scheme_005": "PMAY (Pradhan Mantri Awas Yojana) — Housing for economically weaker sections",
    }
    return scheme_map.get(scheme_id, f"Scheme {scheme_id} not found in knowledge base.")


@tool
def list_available_schemes() -> str:
    """
    List all available government schemes in the knowledge base.
    
    Returns:
        A formatted list of supported schemes.
    """
    schemes = [
        "scheme_001: NSP Pre-Matric Scholarship",
        "scheme_002: PM-KISAN (Farmer Income Support)",
        "scheme_003: Startup India SISFS",
        "scheme_004: PMJAY (Ayushman Bharat)",
        "scheme_005: PMAY (Housing Scheme)",
    ]
    return "\n".join(schemes)


# ═══════════════════════════════════════════════════════════════════════════
# AGENT CONFIGURATION & SETUP
# ═══════════════════════════════════════════════════════════════════════════

def create_policy_navigator_agent():
    """
    Create the Policy-Navigator LangChain agent with tool-calling capabilities.
    """
    # Initialize LLM using Groq (free, fast, and no billing concerns)
    llm = ChatGroq(
        model="llama2-70b-4096",
        temperature=0.1,
        api_key=os.getenv("GROQ_API_KEY")
    )

    # Tools available to the agent
    tools = [
        check_scheme_eligibility,
        get_scheme_info,
        list_available_schemes,
    ]

    # System prompt for the agent
    system_prompt = """You are Policy-Navigator, a Citizen Advocate AI agent for Indian government schemes.

Your role:
- Explain government policies in simple, accessible language
- Verify citizen eligibility for schemes
- Provide step-by-step next actions (Next Best Action — NBA)
- Support Hindi, English, and Hinglish (code-mixed language)
- Generate checklists of required documents

Guidelines:
1. Use available tools to check eligibility and fetch scheme details
2. Explain benefits and eligibility criteria clearly
3. Highlight supporting documents needed
4. Provide encouragement and next steps
5. Always note: "This is informational; consult official sources for final decisions"

Tone: Friendly, helpful, empowering — serving as an advocate for underserved citizens."""

    # Prompt template with chat history
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Create agent executor with tool-calling
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
    )

    return agent_executor


def main():
    """
    Main entry point: Initialize and run the Policy-Navigator agent on Zynd Protocol.
    (Or run locally with fallback mock if SDK unavailable.)
    """
    
    print("\n" + "═" * 70)
    print("  🌐  POLICY-NAVIGATOR — Citizen Advocate Agent")
    print("  " + ("ZyndAI Agent SDK" if ZYND_AVAILABLE else "Local Testing Mode (Fallback)"))
    print("  Aickathon 2026")
    print("═" * 70 + "\n")
    
    if not ZYND_AVAILABLE:
        print("⚠  Note: Running in LOCAL TESTING MODE")
        print("   The ZyndAI Agent SDK is not yet publicly available.")
        print("   This local version demonstrates the agent with LangChain.\n")

    # Step 1: Create Zynd Agent Config
    print("[1/3] Initializing Agent Configuration...")
    agent_config = AgentConfig(
        name="Policy-Navigator",
        description=(
            "Citizen Advocate AI agent for Indian government schemes. "
            "Verifies eligibility, explains policies, and provides next-best actions "
            "via the Zynd Protocol."
        ),
        capabilities={
            "ai": ["nlp", "policy_analysis", "eligibility_verification", "rag"],
            "protocols": ["http", "x402"],
            "services": [
                "scheme_eligibility_check",
                "policy_explanation",
                "document_checklist",
            ],
            "domains": ["governance", "welfare", "india"],
            "languages": ["en", "hi", "hinglish"],
        },
        webhook_host="0.0.0.0",
        webhook_port=5000,
        registry_url="https://registry.zynd.ai",
        price="$0.0001",  # x402 micropayment: 0.0001 USDC per query
        api_key=os.environ.get("ZYND_API_KEY", ""),
        config_dir=".agent-policy-navigator",
    )
    print(f"      ✓ Agent Name: {agent_config.name}")
    print(f"      ✓ Webhook: 0.0.0.0:{agent_config.webhook_port}")
    print(f"      ✓ Price: {agent_config.price} per request\n")

    # Step 2: Initialize ZyndAI Agent
    print("[2/3] Initializing ZyndAI Agent...")
    try:
        zynd_agent = ZyndAIAgent(agent_config=agent_config)
        print("      ✓ ZyndAI Agent created\n")
    except Exception as e:
        print(f"      ⚠  Warning: {e}")
        print("      (Ensure zynd-sdk is installed: pip install zyndai-agent)\n")
        return

    # Step 3: Set up LangChain Agent
    print("[3/3] Setting up LangChain Tool-Calling Agent...")
    try:
        agent_executor = create_policy_navigator_agent()
        zynd_agent.set_langchain_agent(agent_executor)
        print("      ✓ LangChain agent configured with tools\n")
    except Exception as e:
        print(f"      ✗ Failed to create LangChain agent: {e}\n")
        traceback.print_exc()
        return

    # ─────────────────────────────────────────────────────────────────────────
    # Message Handler: Processes queries from Zynd network
    # ─────────────────────────────────────────────────────────────────────────
    def message_handler(message: AgentMessage, topic: str):
        """
        Handle incoming messages from the Zynd network.
        Invokes the LangChain agent and returns responses.
        """
        print(f"\n{'='*70}")
        print(f"[Policy-Navigator] Received Query")
        print(f"Topic: {topic}")
        print(f"Query: {message.content}")
        print(f"{'='*70}\n")

        try:
            # Invoke the LangChain agent
            response = zynd_agent.invoke(message.content, chat_history=[])
            
            print(f"\n[Policy-Navigator] Response:")
            print(f"{response}\n")

            # Send response back via Zynd
            zynd_agent.set_response(message.message_id, response)

        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            print(f"\n[Policy-Navigator] ERROR: {error_msg}\n")
            print(traceback.format_exc())
            zynd_agent.set_response(message.message_id, error_msg)

    # Register message handler
    zynd_agent.add_message_handler(message_handler)

    # ─────────────────────────────────────────────────────────────────────────
    # Agent Running Loop
    # ─────────────────────────────────────────────────────────────────────────
    print("=" * 70)
    print("  ✅  Policy-Navigator Agent is LIVE on Zynd Protocol!")
    print("=" * 70)
    print(f"\n  📍 Agent Name:  {agent_config.name}")
    print(f"  🔗 Webhook:     {zynd_agent.webhook_url}")
    print(f"  💰 Price:       {agent_config.price}")
    print(f"  🛠️  Framework:    LangChain + ZyndAI Agent SDK")
    print(f"\n  Type 'exit' to stop the agent\n")
    print("=" * 70 + "\n")

    # Keep agent running
    try:
        while True:
            user_input = input("\n💬 Your Query (or 'exit', 'status'): ").strip()
            
            if user_input.lower() == "exit":
                print("\n🛑 Shutting down Policy-Navigator agent...\n")
                break
            
            elif user_input.lower() == "status":
                print(f"\n  📊 Agent Status: RUNNING")
                print(f"  🔗 Webhook: {zynd_agent.webhook_url}")
                print(f"  💰 Price: {agent_config.price}")
                print(f"  🛠️  Tools: eligibility_check, scheme_info, list_schemes\n")
            
            elif user_input:
                # Process the query through the agent
                try:
                    print("\n🔄 Processing your query...\n")
                    response = zynd_agent.invoke(user_input, chat_history=[])
                    print(f"\n✅ Agent Response:\n{response}\n")
                except Exception as e:
                    print(f"\n⚠️  Error: {str(e)}\n")
                    print(traceback.format_exc())
    except KeyboardInterrupt:
        print("\n\n🛑 Agent interrupted by user.\n")


if __name__ == "__main__":
    main()
