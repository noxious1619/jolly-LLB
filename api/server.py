"""
api/server.py
FastAPI backend for JOLLY-LLB auto form filler.

Endpoints:
  POST /start-form   → launches Playwright browser at the dummy portal, pauses
  POST /resume-form  → signals Playwright to wake up and fill the form
  GET  /status       → check current session state
  GET  /             → health check
"""

import asyncio
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Resolve absolute path for templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")


# ─── Global session state ────────────────────────────────────────────────────
class FormSession:
    def __init__(self):
        self.event: Optional[asyncio.Event] = None
        self.ready: Optional[asyncio.Event] = None  # set when browser is paused & waiting
        self.user_data: dict = {}
        self.scheme_id: str = ""
        self.status: str = "idle"   # idle | browser_open | filling | done | error
        self.message: str = ""

session = FormSession()


# ─── Request / Response models ────────────────────────────────────────────────
class ZyndTask(BaseModel):
    """
    Standard Zynd A2A Task payload — compatible with the Zynd network protocol.
    Other agents POST this to trigger form-filling on our behalf.

    Both formats are accepted:
      1. Simple (from Streamlit/manual):  {"scheme_id": "...", "user_data": {...}}
      2. Zynd A2A Task (from Zynd agents): {"action": "fill_form", "user_profile": {...}, "scheme_id": "..."}
    """
    # ── Zynd standard fields ────────────────────────────────
    task_id:      Optional[str] = None          # unique task UUID from the calling agent
    agent_did:    Optional[str] = None          # DID of the calling agent (e.g. did:zynd:...)
    action:       Optional[str] = "fill_form"   # always "fill_form" for this endpoint

    # ── Payload — either key works ──────────────────────────
    scheme_id:    str                           # e.g. "scheme_001"
    user_profile: Optional[dict] = None         # Zynd A2A style key
    user_data:    Optional[dict] = None         # Streamlit / simple style key

    def resolved_user_data(self) -> dict:
        """Returns user_profile if provided, else falls back to user_data."""
        return self.user_profile or self.user_data or {}


class StatusResponse(BaseModel):
    status: str
    message: str


# ─── App setup ────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield   # startup / shutdown hooks can go here

app = FastAPI(
    title="JOLLY-LLB Form Filler API",
    description="Automates government scheme form filling via Playwright",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve dummy_portal.html at /static/dummy_portal.html
print(f"[API] Mounting static files from: {TEMPLATES_DIR}")
app.mount("/static", StaticFiles(directory=TEMPLATES_DIR), name="static")


# ─── Endpoints ────────────────────────────────────────────────────────────────
@app.get("/")
async def health():
    return {"status": "ok", "service": "JOLLY-LLB Form Filler API"}


@app.post("/start-form", response_model=StatusResponse)
async def start_form(req: ZyndTask):
    """
    Launches Playwright and opens the government portal for form filling.

    Accepts both:
      - Standard Zynd A2A Task payload  (user_profile + scheme_id + task_id + agent_did)
      - Simple Streamlit payload        (user_data + scheme_id)

    This endpoint is designed to be callable by any Zynd agent via A2A.
    """
    if session.status in ("browser_open", "filling"):
        raise HTTPException(
            status_code=409,
            detail="A form session is already active. Complete or cancel it first."
        )

    try:
        from agents.form_filler import launch_form_filler
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Playwright not installed. Run: pip install playwright && playwright install"
        )

    # Unpack payload — supports both Zynd A2A format and simple format
    resolved_data = req.resolved_user_data()
    if not resolved_data:
        raise HTTPException(status_code=422, detail="user_profile or user_data is required.")

    caller_info = f" | caller: {req.agent_did}" if req.agent_did else ""
    caller_info += f" | task: {req.task_id}" if req.task_id else ""

    session.event     = asyncio.Event()  # resume signal — set by /resume-form
    session.ready     = asyncio.Event()  # readiness signal — set by form_filler when paused
    session.user_data = resolved_data
    session.scheme_id = req.scheme_id
    session.status    = "browser_open"
    session.message   = f"Browser launched. Log in to the portal, then call /resume-form.{caller_info}"

    asyncio.create_task(
        launch_form_filler(
            event=session.event,
            ready=session.ready,
            scheme_id=session.scheme_id,
            user_data=session.user_data,
            on_done=_on_fill_done,
            on_error=_on_fill_error,
        )
    )

    return StatusResponse(status=session.status, message=session.message)


@app.post("/resume-form", response_model=StatusResponse)
async def resume_form():
    """
    Signals the paused Playwright script to wake up and fill the form.
    Waits up to 30s for the browser to be in the paused-and-ready state
    before sending the resume signal, preventing a race condition where
    /resume-form fires before the browser has even finished loading.
    """
    if session.status != "browser_open":
        raise HTTPException(
            status_code=400,
            detail=f"No browser waiting for input. Current status: '{session.status}'"
        )

    # Wait until the form filler signals it is actually paused at event.wait()
    if session.ready and not session.ready.is_set():
        try:
            await asyncio.wait_for(session.ready.wait(), timeout=30.0)
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Browser did not reach the ready-to-fill state within 30s."
            )

    session.event.set()          # ← wakes up the paused Playwright coroutine
    session.status  = "filling"
    session.message = "Form filling in progress..."

    return StatusResponse(status=session.status, message=session.message)


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Returns the current form session status."""
    return StatusResponse(status=session.status, message=session.message)


@app.post("/cancel-form", response_model=StatusResponse)
async def cancel_form():
    """Resets session — call if something goes wrong."""
    session.status  = "idle"
    session.message = "Session cancelled."
    if session.event:
        session.event.set()      # unblock any waiting coroutine
    session.event = None
    return StatusResponse(status=session.status, message=session.message)


# ─── Internal callbacks ───────────────────────────────────────────────────────
def _on_fill_done():
    session.status  = "done"
    session.message = "Form filled and submitted successfully!"


def _on_fill_error(error: str):
    session.status  = "error"
    session.message = f"Error during form fill: {error}"
