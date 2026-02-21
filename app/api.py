# app/api.py
# FastAPI entrypoint for JOLLY-LLB — Policy Navigator Agent
# Exposes /agent (POST) + /health (GET) for Zynd Protocol routing
# and local demo use.
#
# Run:  uvicorn app.api:app --reload --port 8000

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.flow_controller import FlowController

# ─────────────────────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="JOLLY-LLB — Policy Navigator Agent",
    description=(
        "A Citizen Advocate AI that simplifies Indian government schemes, "
        "checks eligibility deterministically, and provides step-by-step "
        "application guidance. Powered by Zynd Protocol + Groq LLaMA 3.3."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# One controller per app instance (holds conversation memory)
controller = FlowController()


# ─────────────────────────────────────────────────────────────
# Request / Response schemas
# ─────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"   # reserved for future multi-session support


class ChatResponse(BaseModel):
    reply: str
    session_id: str


class ResetResponse(BaseModel):
    status: str


# ─────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    """Zynd network liveness probe."""
    return {"status": "ok", "agent": "JOLLY-LLB", "version": "1.0.0"}


@app.post("/agent", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Main Zynd-facing endpoint.
    Accepts a citizen message, runs the full Track-1 → Track-2 pipeline,
    and returns the agent's reply.
    """
    reply = await controller.handle_message(req.message)
    return ChatResponse(reply=reply, session_id=req.session_id)


@app.post("/reset", response_model=ResetResponse)
def reset():
    """Clear conversation memory (start a new session)."""
    controller.reset_conversation()
    return ResetResponse(status="conversation reset")