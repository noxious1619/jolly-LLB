# Policy-Navigator Agent — Zynd Protocol Deployment

Deploy your Policy-Navigator AI agent on the Zynd Protocol using the **ZyndAI Agent SDK** with LangChain tool-calling. This enables your agent to serve Indian citizens queries about government schemes, with micropayment support via x402.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Key new packages:
- **zyndai-agent**: ZyndAI Agent SDK (handles registration, webhooks, x402 payments)
- **langchain-openai**: For OpenAI model integration
- **langchain-classic**: LangChain agent framework

### 2. Set Environment Variables

Create or update your `.env` file:

```bash
# Zynd Protocol API Key
ZYND_API_KEY=your_zynd_api_key_here

# OpenAI API Key (for LLM)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Groq API (alternative to OpenAI)
GROQ_API_KEY=your_groq_api_key_here

# Optional: Demo mode
RUN_DEMO=true
```

### 3. Run the Agent

```bash
python zynd_node.py
```

You should see:
```
═══════════════════════════════════════════════════════════════════════════
  🌐  POLICY-NAVIGATOR — Zynd Protocol Agent Deployment
  ZyndAI Agent SDK  |  Aickathon 2026
═══════════════════════════════════════════════════════════════════════════

[1/3] Initializing Zynd Agent Configuration...
      ✓ Agent Name: Policy-Navigator
      ✓ Webhook: 0.0.0.0:5000
      ✓ Price: $0.0001 per request

[2/3] Initializing ZyndAI Agent...
      ✓ ZyndAI Agent created

[3/3] Setting up LangChain Tool-Calling Agent...
      ✓ LangChain agent configured with tools

═══════════════════════════════════════════════════════════════════════════
  ✅  Policy-Navigator Agent is LIVE on Zynd Protocol!
═══════════════════════════════════════════════════════════════════════════

  📍 Agent Name:  Policy-Navigator
  🔗 Webhook:     http://0.0.0.0:5000
  💰 Price:       $0.0001
  🛠️  Framework:    LangChain + ZyndAI Agent SDK

  Type 'exit' to stop the agent
```

---

## 📋 Agent Capabilities

Your Policy-Navigator agent has the following **LangChain tools**:

### 1. **check_scheme_eligibility**
- Verifies if a citizen is eligible for a specific government scheme
- Uses your eligibility engine and RAG system
- Input: `scheme_id` + `user_profile`
- Output: Eligibility verdict + reasoning

### 2. **get_scheme_info**
- Fetches detailed information about any supported scheme
- Returns eligibility criteria, benefits, required documents
- Input: `scheme_id`
- Output: Scheme details

### 3. **list_available_schemes**
- Lists all available government schemes in the knowledge base
- No input required
- Output: Formatted list of supported schemes

---

## 💬 Example Queries

Users can send queries to your agent via the Zynd network. Examples:

### Query 1: Hindi Eligibility Check
```
"Main ek 25 saal ka OBC student hoon, mera income 50,000 rupees hai. 
Kya main NSP scholarship ke liye eligible hoon?"
```

**Agent Response** (via LangChain tool-calling):
1. Calls `list_available_schemes` to find NSP
2. Calls `check_scheme_eligibility` with user profile
3. Calls `get_scheme_info` for details
4. Returns: Eligibility status + next steps + documents needed

### Query 2: Farmer Income Support
```
"PM KISAN se kitna paisa milega? Mere paas 2 hectare zameen hai."
```

**Agent Response**:
1. Calls `get_scheme_info` for PM-KISAN
2. Calls `check_scheme_eligibility` with farmer profile
3. Returns: Benefit amount + eligibility status

### Query 3: Startup Funding
```
"Mere startup ko Startup India Seed Fund se funding kaise milegi?"
```

---

## 🔧 Configuration

Edit `AGENT_CONFIG` in `zynd_node.py` to customize:

```python
agent_config = AgentConfig(
    name="Policy-Navigator",                       # Agent name
    description="Citizen Advocate AI agent...",    # Description for registry
    capabilities={...},                            # Supported capabilities
    webhook_host="0.0.0.0",                        # Webhook listener host
    webhook_port=5000,                             # Webhook listener port
    registry_url="https://registry.zynd.ai",       # Zynd registry URL
    price="$0.0001",                               # x402 micropayment price
    api_key=os.environ["ZYND_API_KEY"],           # Your Zynd API key
    config_dir=".agent-policy-navigator",          # Config directory
)
```

---

## 🛠️ How It Works

### Message Flow

```
Zynd Network
    ↓
[ZyndAI Agent SDK]
    ↓
Webhook Listener (port 5000)
    ↓
message_handler() function
    ↓
LangChain Tool-Calling Agent
    ↓
[choose_tool] check_scheme_eligibility | get_scheme_info | list_available_schemes
    ↓
[invoke tool]
    ↓
Parse result
    ↓
zynd_agent.set_response() ← send back via Zynd
```

### Tool-Calling Loop

1. **User sends query** via Zynd network
2. **message_handler receives** the query
3. **LangChain agent evaluates** which tools to call
4. **Tools execute** and return results
5. **Agent synthesizes** final response
6. **Response sent back** to user via Zynd x402 protocol

---

## 📊 Agent Architecture

```
┌─────────────────────────────────────────────────────┐
│            Policy-Navigator Agent                   │
├─────────────────────────────────────────────────────┤
│  ZyndAI Agent Framework (webhook + registry)       │
│  ├─ Webhook Listener on port 5000                  │
│  ├─ Auto-registration on Zynd registry             │
│  ├─ x402 micropayment handling                     │
│  └─ Message routing                               │
├─────────────────────────────────────────────────────┤
│  LangChain Tool-Calling Agent                      │
│  ├─ GPT-4O or Groq LLM                            │
│  ├─ Tool selection & execution                    │
│  └─ Chat memory (optional)                        │
├─────────────────────────────────────────────────────┤
│  Tools                                             │
│  ├─ check_scheme_eligibility()                    │
│  ├─ get_scheme_info()                             │
│  └─ list_available_schemes()                      │
├─────────────────────────────────────────────────────┤
│  Backend Integration                              │
│  ├─ ask_agent_with_eligibility() (RAG + Rules)   │
│  ├─ FAISS Vector DB                              │
│  ├─ Eligibility Engine                           │
│  └─ Next-Best-Action (NBA)                       │
└─────────────────────────────────────────────────────┘
```

---

## 🧪 Testing the Agent Locally

### Method 1: Command-Line Loop
```bash
python zynd_node.py

# In the running agent terminal, type:
Command: status
  → Agent Status: RUNNING
  → Webhook: http://0.0.0.0:5000

Command: exit
```

### Method 2: Send HTTP Requests (Testing)
While the agent is running, test the webhook:

```bash
curl -X POST http://localhost:5000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "test-123",
    "content": "Kya main PM KISAN ke liye eligible hoon?",
    "topic": "scheme_query"
  }'
```

---

## 🌐 Deployment on Zynd Network

### Step 1: Register Your Agent
```bash
python zynd_node.py
```
The agent auto-registers on the Zynd registry under:
- **Agent Name**: Policy-Navigator
- **DID**: Generated automatically
- **Registry**: https://registry.zynd.ai
- **Webhook**: Your configured host/port

### Step 2: Keep Agent Running
Use a process manager for production:

```bash
# Using screen
screen -S policy-navigator
python zynd_node.py
# Ctrl+A then D to detach

# Using tmux
tmux new-session -d -s policy-navigator "cd /path/to/agent && python zynd_node.py"

# Using PM2 (Node.js)
pm2 start "python zynd_node.py" --name "policy-navigator"
```

### Step 3: Test via Zynd Network
Once registered, other agents and users can query your agent via the Zynd Protocol!

---

## 💰 Micropayments (x402)

Your agent charges **$0.0001 USDC** per query via the x402 protocol. The ZyndAI Agent SDK handles:
- Payment collection
- Micropayment routing
- Transaction logging

No additional code needed—already built into `AgentConfig(price="$0.0001")`.

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'zyndai_agent'`
**Solution**: Install the SDK
```bash
pip install zyndai-agent
```

### Issue: Webhook not responding
**Ensure**:
- Port 5000 is not in use: `lsof -i :5000` (Linux/Mac) or `netstat -ano | findstr :5000` (Windows)
- Firewall allows inbound connections on port 5000
- Agent is running (see "RUNNING" message)

### Issue: Tool execution fails
**Debug**:
1. Check `.env` has `ZYND_API_KEY` and `OPENAI_API_KEY`
2. Verify eligibility engine is working: `python verify_track2.py`
3. Check FAISS index exists: `ls -la faiss_index/`

### Issue: Cryptocurrency/USDC issues
**Note**: x402 micropayments use testnet by default. For mainnet, update:
```python
agent_config = AgentConfig(..., mainnet=True)
```

---

## 📚 Further Reading

- [Zynd Protocol Docs](https://docs.zynd.ai)
- [ZyndAI Agent SDK GitHub](https://github.com/zynd/agent-sdk)
- [LangChain Tool-Calling Agent](https://python.langchain.com/docs/modules/agents/)
- [x402 Micropayment Protocol](https://x402.org)

---

## 📞 Support

For issues or questions:
1. Check `.env` configuration
2. Review agent logs: `python zynd_node.py 2>&1 | tee agent.log`
3. Test backend eligibility engine: `python verify_track2.py`
4. Open issue on repository with:
   - Error message
   - Agent logs excerpt
   - `.env` config (without keys)

---

**Happy Deploying! 🎉 Your Policy-Navigator agent is now a member of the Zynd Protocol network.**
