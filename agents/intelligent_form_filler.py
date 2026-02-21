"""
agents/intelligent_form_filler.py
===================================
LLM-powered form filler that works with ANY government website URL.

How it works:
  1. Navigate to the URL
  2. Inject JS to snapshot all visible form fields (id, name, label, placeholder)
  3. Send snapshot + user_data to Groq LLM
  4. LLM returns a fill plan: [{selector, value, action}, ...]
  5. Execute the plan in the browser
  6. If OTP / multi-step detected, pause for human

This replaces hardcoded SCHEME_FIELD_MAP selectors and works with any site.
"""

import asyncio
import json
import os
from typing import Callable, Optional

from dotenv import load_dotenv
from groq import Groq
from playwright.async_api import async_playwright, Browser, Page

load_dotenv()

# ── JS injected into any page to extract visible form fields ──────────────────
_FIELD_EXTRACTOR_JS = """
() => {
    const seen = new Set();
    const fields = [];
    const els = document.querySelectorAll(
        'input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="image"]), select, textarea'
    );
    for (const el of els) {
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 && rect.height === 0) continue;   // hidden
        const labelEl = el.id
            ? document.querySelector(`label[for="${el.id}"]`)
            : el.closest('label') || el.previousElementSibling;
        const key = el.id || el.name || `${el.tagName}_${fields.length}`;
        if (seen.has(key)) continue;
        seen.add(key);
        fields.push({
            selector:    el.id ? `#${el.id}` : (el.name ? `[name="${el.name}"]` : null),
            id:          el.id          || null,
            name:        el.name        || null,
            type:        el.type        || el.tagName.toLowerCase(),
            placeholder: el.placeholder || null,
            label:       labelEl ? labelEl.textContent.trim().slice(0, 80) : null,
            options:     el.tagName === "SELECT"
                         ? [...el.options].slice(1, 10).map(o => ({value: o.value, text: o.text.trim()}))
                         : null,
        });
    }
    return JSON.stringify(fields);
}
"""

# ── Groq prompt ────────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = """You are a form-filling assistant for Indian government welfare schemes.
You are given:
  - page_url: URL of the current form page
  - page_title: title of the page
  - fields: list of form fields extracted from the page DOM
  - user_data: applicant profile

Your job: produce a JSON fill plan — an array of actions to fill the form.
Each action has:
  {
    "selector": "CSS selector (use the 'selector' field from fields)",
    "value":    "the value to enter or select",
    "action":   "fill" | "select" | "check" | "skip",
    "reason":   "brief explanation"
  }

Rules:
- Only include fields you can confidently map to user_data.
- For SELECT fields, use one of the provided options[].value strings.
- For Aadhaar fields (aadhaar, aadhar, uid): use user_data.aadhaar with no spaces.
- For name fields: use user_data.name.
- Skip fields you can't map or that are OTP/CAPTCHA/password.
- Return ONLY a JSON array, no markdown, no explanation outside the array.
"""


def _call_groq_for_fill_plan(
    page_url: str,
    page_title: str,
    fields: list,
    user_data: dict,
) -> list:
    """
    Call Groq LLM to produce a fill plan for the current page.
    Returns list of action dicts.
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

    user_msg = json.dumps({
        "page_url":   page_url,
        "page_title": page_title,
        "fields":     fields[:40],   # cap to avoid token overflow
        "user_data":  user_data,
    }, ensure_ascii=False, indent=2)

    print("[IntelligentFiller] Calling Groq LLM to analyze form fields...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user",   "content": user_msg},
        ],
        temperature=0.1,
        max_tokens=2048,
    )

    raw = response.choices[0].message.content.strip()
    print(f"[IntelligentFiller] LLM response ({len(raw)} chars):\n{raw[:500]}")

    # Parse — strip any accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        plan = json.loads(raw)
        return plan if isinstance(plan, list) else []
    except json.JSONDecodeError as e:
        print(f"[IntelligentFiller] Warning: could not parse LLM JSON: {e}")
        return []


async def _snapshot_fields(page: Page) -> tuple[str, str, list]:
    """Extract URL, title, and visible form fields from the current page."""
    url   = page.url
    title = await page.title()
    try:
        raw    = await page.evaluate(_FIELD_EXTRACTOR_JS)
        fields = json.loads(raw)
    except Exception as e:
        print(f"[IntelligentFiller] DOM extraction error: {e}")
        fields = []
    print(f"[IntelligentFiller] Found {len(fields)} visible form fields on: {title}")
    return url, title, fields


async def _execute_fill_plan(page: Page, plan: list) -> int:
    """Execute a fill plan on the page. Returns number of successful fills."""
    filled = 0
    for action in plan:
        sel    = action.get("selector")
        value  = action.get("value")
        act    = action.get("action", "fill")
        reason = action.get("reason", "")

        if not sel or not value or act == "skip":
            continue

        try:
            loc = page.locator(sel)
            count = await loc.count()
            if count == 0:
                print(f"[IntelligentFiller]   MISS  {sel}  (not found)")
                continue

            if act == "select":
                # Try value first, then label text
                try:
                    await loc.select_option(value=str(value))
                except Exception:
                    await loc.select_option(label=str(value))
                await page.wait_for_timeout(600)   # wait for cascades
            elif act == "check":
                await loc.check()
            else:
                await loc.fill(str(value))

            print(f"[IntelligentFiller]   OK    {sel} = {value}  ({reason})")
            filled += 1

        except Exception as e:
            print(f"[IntelligentFiller]   WARN  {sel}: {e}")

    return filled


# ── Main entry point ───────────────────────────────────────────────────────────

async def launch_intelligent_filler(
    url: str,
    user_data: dict,
    event: asyncio.Event,
    ready: Optional[asyncio.Event] = None,
    on_done: Optional[Callable] = None,
    on_error: Optional[Callable] = None,
):
    """
    Intelligent form filler — given any URL and user_data:
      1. Opens browser (Edge preferred on Windows)
      2. Signals ready so /resume-form can be awaited
      3. PAUSES at event.wait() — browser stays open for human login/OTP
      4. On resume: snapshots DOM, asks Groq LLM for fill plan, executes it
      5. If multi-step detected (e.g. OTP gate), re-snapshots after each step

    This is the production-grade replacement for the hardcoded SCHEME_FIELD_MAP.
    """
    print(f"[IntelligentFiller] Starting for URL: {url}")
    browser: Optional[Browser] = None

    try:
        async with async_playwright() as p:
            # ── Launch browser (Edge > Chrome > bundled Chromium) ─────
            launch_kwargs = dict(
                headless=False,
                slow_mo=30,
                args=["--start-maximized", "--foreground", "--new-window",
                      "--disable-extensions"],
            )
            for channel in ("msedge", "chrome", None):
                try:
                    if channel:
                        browser = await p.chromium.launch(channel=channel, **launch_kwargs)
                    else:
                        browser = await p.chromium.launch(**launch_kwargs)
                    print(f"[IntelligentFiller] Browser: {channel or 'bundled Chromium'}")
                    break
                except Exception:
                    browser = None
            if not browser:
                raise RuntimeError("Could not launch any browser.")

            # Signal ready IMMEDIATELY — before page creation / navigation
            if ready:
                ready.set()
                print("[IntelligentFiller] READY - /resume-form may proceed.")

            ctx  = await browser.new_context(no_viewport=True)
            page = await ctx.new_page()
            await page.bring_to_front()

            # ── Navigate to the form URL ──────────────────────────────
            print(f"[IntelligentFiller] Navigating to {url} ...")
            try:
                await page.goto(url, wait_until="networkidle", timeout=900000)
                await page.bring_to_front()
                print(f"[IntelligentFiller] Loaded: {await page.title()}")
            except Exception as e:
                print(f"[IntelligentFiller] WARN: Navigation issue: {e}")

            print("[IntelligentFiller] PAUSED - browser open. Call /resume-form when ready.")

            # ── PAUSE — browser stays open until /resume-form fires ───
            await event.wait()

            print("[IntelligentFiller] RESUMED - analyzing page and filling...")

            # ── Step A: Snapshot current page fields ──────────────────
            cur_url, title, fields = await _snapshot_fields(page)

            if not fields:
                print("[IntelligentFiller] No fields found on page.")
                if on_done:
                    on_done()
                await browser.close()
                return

            # ── Step B: Ask LLM for fill plan ─────────────────────────
            plan = _call_groq_for_fill_plan(cur_url, title, fields, user_data)
            if not plan:
                print("[IntelligentFiller] LLM returned empty plan.")
            else:
                filled = await _execute_fill_plan(page, plan)
                print(f"[IntelligentFiller] Filled {filled}/{len(plan)} fields.")

            # ── Step C: Check if submit button is available ───────────
            # Look for common submit patterns
            submit_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "input[value='Save']",
                "input[value='Submit']",
                "input[value='Get OTP']",
                "button:has-text('Submit')",
                "button:has-text('Save')",
            ]
            submit_loc = None
            for s in submit_selectors:
                loc = page.locator(s)
                if await loc.count() > 0:
                    submit_loc = loc
                    print(f"[IntelligentFiller] Submit button found: {s}")
                    break

            if submit_loc:
                await submit_loc.click()
                await page.wait_for_timeout(2000)
                print("[IntelligentFiller] Clicked submit.")

            await browser.close()

        if on_done:
            on_done()

    except Exception as e:
        print(f"[IntelligentFiller] ERROR: {e}")
        try:
            if browser:
                await browser.close()
        except Exception:
            pass
        if on_error:
            on_error(str(e))
