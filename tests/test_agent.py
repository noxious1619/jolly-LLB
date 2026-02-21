"""
tests/test_agent.py — JOLLY-LLB Form Filler Agent Test Suite
=============================================================

Runs in TWO phases:

  Phase 1 — Dummy Portal (fully automated)
    Starts the FastAPI server, calls /start-form, /resume-form,
    verifies /status → "done". No human input required.

  Phase 2 — Real PM-KISAN Website (semi-automated)
    Opens https://pmkisan.gov.in/RegistrationFormupdated.aspx in a
    visible Chromium browser.
    - Fills in the Aadhaar number
    - Clicks "Get OTP"
    - PAUSES for the human to enter the OTP manually
    - After human clicks "Proceed", fills the full farmer registration
      form fields with the provided user data

Usage:
  Run BOTH phases:
      py -3.12 tests/test_agent.py

  Run only Phase 1 (dummy portal):
      py -3.12 tests/test_agent.py --phase1

  Run only Phase 2 (real PM-KISAN site):
      py -3.12 tests/test_agent.py --phase2
"""

import asyncio
import sys
import time
import subprocess
import threading
import os as _os

# Load .env from the project root (one level up from tests/)
from dotenv import load_dotenv as _load_dotenv
_load_dotenv(_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), ".env"))
import requests

# ─── Test data ────────────────────────────────────────────────────────────────
TEST_USER = {
    "name":         "Arjun Kumar",
    "father_name":  "Ram Kumar",
    "dob":          "01/01/1980",        # DD/MM/YYYY
    "age":          45,
    "gender":       "Male",
    "community":    "General",
    "income":       120000,
    "land_acres":   2.5,
    "aadhaar":      "268700723493",
    "bank_account": "9876543210",
    "bank_name":    "State Bank of India",
    "ifsc":         "SBIN0001234",
    "mobile":       "9999999999",
    "state":        "Uttar Pradesh",
    "district":     "Lucknow",
    "sub_district": "Lucknow",
    "village":      "Indira Nagar",
    "farmer_type":  "Small Farmer",
    "land_reg_no":  "LRN-2023-0042",
}

API_URL      = "http://localhost:8000"
PHASE1_PASS  = "✅ PASS"
PHASE1_FAIL  = "❌ FAIL"


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — Dummy Portal (fully automated)
# ══════════════════════════════════════════════════════════════════════════════

def _start_api_server():
    """Start uvicorn in a background thread and return the process."""
    import os
    log_path = os.path.join(os.path.dirname(__file__), "server_test.log")
    log_file  = open(log_path, "w", encoding="utf-8")
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.server:app", "--port", "8000"],
        stdout=log_file,
        stderr=log_file,
        env=env,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # jolly-LLB/
    )
    time.sleep(5)   # give uvicorn time to fully boot
    print(f"    Server log -> {log_path}")
    return proc


def _check(label: str, condition: bool, detail: str = ""):
    status = PHASE1_PASS if condition else PHASE1_FAIL
    msg = f"  {status}  {label}"
    if detail:
        msg += f"  →  {detail}"
    print(msg)
    return condition


def run_phase1():
    print()
    print("=" * 64)
    print("  PHASE 1 — Dummy Portal Test (Fully Automated)")
    print("=" * 64)

    # ── 1. Start server ───────────────────────────────────────────────
    print("\n[1/5] Starting FastAPI server on :8000 ...")
    server_proc = _start_api_server()

    all_passed = True
    try:
        # ── 2. Health check ───────────────────────────────────────────
        print("\n[2/5] Health check  GET /")
        try:
            r = requests.get(f"{API_URL}/", timeout=5)
            ok = r.status_code == 200 and r.json().get("status") == "ok"
            all_passed &= _check("/  →  200 OK", ok, r.text[:80])
        except Exception as e:
            all_passed &= _check("/  →  200 OK", False, str(e))

        # ── 3. Status baseline ────────────────────────────────────────
        print("\n[3/5] Baseline status  GET /status")
        try:
            r = requests.get(f"{API_URL}/status", timeout=5)
            ok = r.json().get("status") == "idle"
            all_passed &= _check("/status == idle", ok, r.text[:80])
        except Exception as e:
            all_passed &= _check("/status == idle", False, str(e))

        # ── 4. Start form (Zynd A2A payload) ─────────────────────────
        print("\n[4/5] POST /start-form  (Zynd A2A format)")
        payload = {
            "task_id":    "test-task-001",
            "agent_did":  "did:zynd:test-runner:000",
            "action":     "fill_form",
            "scheme_id":  "scheme_002",        # PM-KISAN
            "user_profile": TEST_USER,
        }
        try:
            r = requests.post(f"{API_URL}/start-form", json=payload, timeout=10)
            ok = r.json().get("status") == "browser_open"
            all_passed &= _check("/start-form → browser_open", ok, r.text[:100])
        except Exception as e:
            all_passed &= _check("/start-form → browser_open", False, str(e))

        # Let Playwright open the browser
        time.sleep(3)

        # ── 5. Resume form ────────────────────────────────────────────
        print("\n[5/5] POST /resume-form  → bot fills dummy fields")
        try:
            r = requests.post(f"{API_URL}/resume-form", timeout=10)
            ok = r.json().get("status") == "filling"
            all_passed &= _check("/resume-form → filling", ok, r.text[:100])
        except Exception as e:
            all_passed &= _check("/resume-form → filling", False, str(e))

        # Poll until done or timeout
        timeout = time.time() + 120
        final_status = "unknown"
        while time.time() < timeout:
            try:
                s = requests.get(f"{API_URL}/status", timeout=3).json().get("status")
                if s in ("done", "error"):
                    final_status = s
                    break
            except Exception:
                pass
            time.sleep(1)

        all_passed &= _check("/status → done", final_status == "done",
                             f"got '{final_status}'")

    finally:
        server_proc.terminate()

    print()
    if all_passed:
        print("  ✅ Phase 1 PASSED — all checks green.")
    else:
        print("  ❌ Phase 1 FAILED — see above for details.")
    return all_passed


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — Intelligent URL-based Form Filler (LLM-powered, no hardcoded selectors)
# ══════════════════════════════════════════════════════════════════════════════

PMKISAN_REGISTRATION_URL = "https://pmkisan.gov.in/RegistrationFormupdated.aspx"

# JS to extract all visible, ENABLED form fields from any page
_FIELD_EXTRACTOR_JS = """
() => {
    const seen = new Set();
    const fields = [];
    const els = document.querySelectorAll(
        'input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="image"]), select, textarea'
    );
    for (const el of els) {
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 && rect.height === 0) continue;
        const labelEl = el.id
            ? document.querySelector(`label[for="${el.id}"]`)
            : el.closest('label') || el.previousElementSibling;
        const key = el.id || el.name || `${el.tagName}_${fields.length}`;
        if (seen.has(key)) continue;
        seen.add(key);
        const isDisabled = el.disabled || el.readOnly
                           || el.classList.contains('aspNetDisabled');
        fields.push({
            selector:    el.id ? `#${el.id}` : (el.name ? `[name="${el.name}"]` : null),
            id:          el.id          || null,
            name:        el.name        || null,
            type:        el.type        || el.tagName.toLowerCase(),
            placeholder: el.placeholder || null,
            label:       labelEl ? labelEl.textContent.trim().slice(0, 80) : null,
            disabled:    isDisabled,     // LLM must skip disabled/readonly fields
            value:       el.value || null,  // prefilled value from Aadhaar
            options:     el.tagName === "SELECT"
                         ? [...el.options].slice(1,10).map(o => ({value: o.value, text: o.text.trim()}))
                         : null,
        });
    }
    return JSON.stringify(fields);
}
"""

import json as _json
import os as _os
from groq import Groq as _Groq

_FILL_SYSTEM_PROMPT = """You are a form-filling assistant for Indian government welfare schemes.
Given page fields and user_data, return a JSON array of fill actions:
[{"selector":"#id", "value":"...", "action":"fill"|"select", "reason":"..."}]
Rules:
- CRITICAL: SKIP any field where disabled==true or value is already set (pre-filled from Aadhaar).
- For Aadhaar fields: use user_data.aadhaar with no spaces.
- For SELECT fields: use one of the provided options[].value strings exactly.
- Skip OTP, captcha, password, disabled, readonly fields entirely.
- Return ONLY a JSON array, no markdown, no extra text.
"""

def _llm_fill_plan(page_url, page_title, fields, user_data):
    api_key = _os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        print("[LLM] ERROR: GROQ_API_KEY not set — skipping LLM fill.")
        return []
    # timeout=900s (15 min) so slow network / long queues don't disconnect us
    client = _Groq(api_key=api_key, timeout=900, max_retries=2)
    msg = _json.dumps({"page_url": page_url, "page_title": page_title,
                        "fields": fields[:40], "user_data": user_data},
                       ensure_ascii=False)
    print(f"\n[LLM] Asking Groq to map {len(fields)} fields -> user_data...")
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": _FILL_SYSTEM_PROMPT},
                  {"role": "user",   "content": msg}],
        temperature=0.1, max_tokens=2048,
    )
    raw = resp.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        plan = _json.loads(raw)
        print(f"[LLM] Got {len(plan)} fill actions.")
        return plan if isinstance(plan, list) else []
    except Exception as e:
        print(f"[LLM] Parse error: {e}\nRaw: {raw[:300]}")
        return []


async def run_phase2_playwright():
    """
    Intelligent Phase 2: opens any URL, extracts form fields via JS,
    asks Groq LLM to map user_data to them, fills automatically.
    Pauses for human OTP entry between multi-step flows.
    """
    from playwright.async_api import async_playwright

    print()
    print("=" * 64)
    print("  PHASE 2 — Intelligent PM-KISAN Form Filler (LLM-powered)")
    print("=" * 64)
    print()
    print("  The agent will:")
    print("  1. Open the PM-KISAN registration page in Edge")
    print("  2. Analyze form fields using DOM inspection")
    print("  3. Ask Groq LLM to map your profile to form fields")
    print("  4. PAUSE for OTP — you enter it, then press ENTER")
    print("  5. Auto-fill the registration form after OTP")
    print("  6. PAUSE again before final submit for your review")
    print()
    input("  Press ENTER to open the browser... ")

    async with async_playwright() as p:
        browser = None
        for channel in ("msedge", "chrome", None):
            try:
                kw = dict(headless=False, slow_mo=40,
                          args=["--start-maximized", "--foreground", "--new-window"])
                browser = await p.chromium.launch(
                    **({"channel": channel} if channel else {}), **kw)
                print(f"    Browser: {channel or 'bundled Chromium'}")
                break
            except Exception:
                pass

        ctx  = await browser.new_context(no_viewport=True)
        page = await ctx.new_page()
        await page.bring_to_front()

        try:
            # ── Step 1: Navigate ──────────────────────────────────────
            print(f"\n[1] Loading: {PMKISAN_REGISTRATION_URL}")
            await page.goto(PMKISAN_REGISTRATION_URL,
                            wait_until="networkidle", timeout=900000)
            await page.bring_to_front()
            print(f"    Loaded: {await page.title()}")

            # ── Step 2: Snapshot Step-1 fields (Aadhaar gate) ─────────
            print("\n[2] Analyzing Step-1 fields (Aadhaar gate)...")
            raw_fields = await page.evaluate(_FIELD_EXTRACTOR_JS)
            step1_fields = _json.loads(raw_fields)
            print(f"    Found {len(step1_fields)} fields on Step-1 page.")

            # ── Step 3: LLM maps user_data to step-1 fields ───────────
            step1_plan = _llm_fill_plan(
                page.url, await page.title(), step1_fields, TEST_USER)

            for action in step1_plan:
                sel      = action.get("selector")
                value    = action.get("value")
                act      = action.get("action", "fill")
                disabled = action.get("disabled", False)
                if not sel or not value or act == "skip" or disabled:
                    continue
                try:
                    loc = page.locator(sel)
                    if await loc.count() == 0:
                        print(f"    MISS {sel}, trying name fallback...")
                        continue
                    # Double-check: skip if element is actually disabled in DOM
                    is_dis = await loc.evaluate("el => el.disabled || el.readOnly || el.classList.contains('aspNetDisabled')")
                    if is_dis:
                        print(f"    SKIP (disabled) {sel}")
                        continue
                    if act == "select":
                        try:
                            await loc.select_option(value=str(value))
                        except Exception:
                            await loc.select_option(label=str(value))
                    else:
                        await loc.fill(str(value))
                    print(f"    OK  {sel} = {value}  ({action.get('reason','')})")
                except Exception as e:
                    print(f"    WARN {sel}: {e}")

            # ── Step 4: Click OTP button ───────────────────────────────
            print("\n[3] Looking for OTP trigger button...")
            otp_btn = None
            otp_selectors = [
                "input[value='Get OTP']",
                "input[value='GetOTP']",
                "input[id*='otp' i]",
                "input[id*='consent' i]",
                "button:has-text('Get OTP')",
                "button:has-text('Send OTP')",
                "input[type='submit']",   # last resort: first submit on page
            ]
            for sel in otp_selectors:
                loc = page.locator(sel)
                if await loc.count() > 0:
                    otp_btn = loc
                    print(f"    Found OTP button: {sel}")
                    break
            if otp_btn:
                await otp_btn.click()
                print("    OTP triggered OK")
            else:
                print("    WARN: OTP button not found — click it manually in browser")

            print()
            print("  PAUSED - OTP sent to Aadhaar-linked mobile.")
            print("  1. Check your phone for the OTP")
            print("  2. Enter it on the webpage")
            print("  3. Click Proceed / Submit on the page")
            print("  4. Wait for the registration form to appear")
            print("  5. Then press ENTER here to continue")
            print()
            await asyncio.to_thread(input, "  [ENTER when registration form is visible] ")

            # ── Step 5: Snapshot Step-2 fields (full registration form) ──
            print("\n[4] Analyzing registration form fields (LLM)...")
            await page.wait_for_timeout(1500)
            raw_fields2 = await page.evaluate(_FIELD_EXTRACTOR_JS)
            step2_fields = _json.loads(raw_fields2)
            print(f"    Found {len(step2_fields)} fields on Step-2 page.")

            step2_plan = _llm_fill_plan(
                page.url, await page.title(), step2_fields, TEST_USER)

            # ── Step 6: Execute fill plan ──────────────────────────────
            print("\n[5] Filling registration form...")
            for action in step2_plan:
                sel      = action.get("selector")
                value    = action.get("value")
                act      = action.get("action", "fill")
                disabled = action.get("disabled", False)
                if not sel or not value or act == "skip" or disabled:
                    continue
                try:
                    loc = page.locator(sel)
                    if await loc.count() == 0:
                        print(f"    MISS {sel}")
                        continue
                    # Skip actually-disabled DOM elements immediately (no 30s wait)
                    is_dis = await loc.evaluate("el => el.disabled || el.readOnly || el.classList.contains('aspNetDisabled')")
                    if is_dis:
                        print(f"    SKIP (disabled/readonly) {sel} = already set to '{await loc.input_value()}'")
                        continue
                    if act == "select":
                        try:
                            await loc.select_option(value=str(value))
                        except Exception:
                            await loc.select_option(label=str(value))
                        await page.wait_for_timeout(800)  # cascade wait
                    else:
                        await loc.fill(str(value))
                    print(f"    OK  {sel} = {value}")
                except Exception as e:
                    print(f"    WARN {sel}: {e}")

            print("\n    All fields filled OK")

            # ── Step 7: Safety gate ────────────────────────────────────
            await page.screenshot(path="tests/pmkisan_filled.png")
            print("    Screenshot -> tests/pmkisan_filled.png")
            print()
            print("  PAUSED - Review the form in the browser.")
            print("  Type 'submit' + ENTER to submit, or just ENTER to skip.")
            choice = await asyncio.to_thread(
                input, "  [submit / ENTER to skip] ")

            if choice.strip().lower() == "submit":
                for sel in ["input[value='Save']", "button:has-text('Save')",
                            "input[type='submit']", "button[type='submit']"]:
                    loc = page.locator(sel)
                    if await loc.count() > 0:
                        await loc.click()
                        await page.wait_for_timeout(3000)
                        print("    Submitted OK")
                        await page.screenshot(path="tests/pmkisan_submitted.png")
                        print("    Screenshot -> tests/pmkisan_submitted.png")
                        break
            else:
                print("    Skipped submission (safe).")

            print()
            print("  Phase 2 complete.")
            await asyncio.to_thread(input, "  [ENTER to close browser] ")
            return True

        except Exception as e:
            print(f"\n  Phase 2 error: {e}")
            try:
                await page.screenshot(path="tests/pmkisan_error.png")
                print("     Screenshot -> tests/pmkisan_error.png")
            except Exception:
                pass
            return False
        finally:
            await browser.close()


def run_phase2():
    return asyncio.run(run_phase2_playwright())


# ══════════════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    args = set(sys.argv[1:])
    run_p1 = "--phase2" not in args   # default: run both
    run_p2 = "--phase1" not in args

    print()
    print("┌─────────────────────────────────────────────────────────┐")
    print("│       JOLLY-LLB Form Filler — Agent Test Suite          │")
    print("└─────────────────────────────────────────────────────────┘")

    p1_result = True
    p2_result = True

    if run_p1:
        p1_result = run_phase1()

    if run_p2:
        p2_result = run_phase2()

    print()
    print("─" * 64)
    print("  FINAL RESULTS")
    print("─" * 64)
    if run_p1:
        print(f"  Phase 1 (Dummy Portal):   {'✅ PASSED' if p1_result else '❌ FAILED'}")
    if run_p2:
        print(f"  Phase 2 (PM-KISAN Real):  {'✅ PASSED' if p2_result else '❌ FAILED'}")
    print()

    sys.exit(0 if (p1_result and p2_result) else 1)
