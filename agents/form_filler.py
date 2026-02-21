"""
agents/form_filler.py
Playwright-based browser automation for JOLLY-LLB.

Key design principle:
  The browser is GUARANTEED to stay open until /resume-form is called,
  regardless of page load speed or selector availability. This is
  achieved by awaiting the asyncio.Event BEFORE any form interaction.

Flow:
  1. Open Chromium (visible)
  2. Navigate to the portal
  3. ── PAUSE ── await event.wait()  ← browser stays open here indefinitely
  4. RESUME when /resume-form sets the event
  5. Fill form fields, submit
"""

import asyncio
from typing import Callable, Optional
from playwright.async_api import async_playwright, Browser, Page

# URL of the dummy portal served by FastAPI's StaticFiles
PORTAL_URL = "http://localhost:8000/static/dummy_portal.html"

# Maps scheme_id → CSS selectors in the dummy portal HTML
SCHEME_FIELD_MAP = {
    "scheme_001": {   # NSP Pre-Matric Scholarship
        "name":         "#applicant-name",
        "age":          "#applicant-age",
        "community":    "#applicant-community",
        "income":       "#family-income",
        "class_level":  "#class-level",
        "school_name":  "#school-name",
        "aadhaar":      "#aadhaar-number",
        "bank_account": "#bank-account",
    },
    "scheme_002": {   # PM-KISAN
        "name":         "#applicant-name",
        "age":          "#applicant-age",
        "land_acres":   "#land-acres",
        "income":       "#family-income",
        "aadhaar":      "#aadhaar-number",
        "bank_account": "#bank-account",
    },
    "scheme_003": {   # Startup India SISFS
        "name":         "#applicant-name",
        "startup_name": "#startup-name",
        "dpiit_number": "#dpiit-number",
        "email":        "#email",
        "bank_account": "#bank-account",
    },
}


async def _safe_fill(page: Page, selector: str, value: str, key: str):
    """Fill a field silently - log success/failure, never raise."""
    try:
        loc = page.locator(selector)
        tag = await loc.evaluate("el => el.tagName.toLowerCase()")
        if tag == "select":
            await loc.select_option(str(value))
        else:
            await loc.fill(str(value))
        print(f"[FormFiller]   OK  {key} = {value}")
    except Exception as e:
        print(f"[FormFiller]   SKIP '{key}' ({selector}): {e}")


async def launch_form_filler(
    event: asyncio.Event,
    scheme_id: str,
    user_data: dict,
    on_done: Optional[Callable] = None,
    on_error: Optional[Callable] = None,
    ready: Optional[asyncio.Event] = None,
):
    """
    Main coroutine — runs as a background asyncio.Task in the FastAPI loop.

    The browser window STAYS OPEN at all times between /start-form and
    /resume-form. The only thing that closes it is a crash or explicit
    browser.close() after submit.
    """
    print(f"\n[FormFiller] Starting for scheme: {scheme_id}")

    browser: Optional[Browser] = None

    try:
        async with async_playwright() as p:
            # ── 1. Launch browser ─────────────────────────────────────
            # On Windows, bundled Chromium launched from a subprocess does NOT
            # get foreground window rights. Using the installed system browser
            # (Edge or Chrome) solves this — Windows treats them as real apps.
            launch_kwargs = dict(
                headless=False,
                slow_mo=500,            # 500ms between actions — visible typing speed
                args=[
                    "--start-maximized",
                    "--foreground",
                    "--new-window",
                    "--disable-extensions",
                ],
            )
            for channel in ("msedge", "chrome", None):
                try:
                    if channel:
                        browser = await p.chromium.launch(channel=channel, **launch_kwargs)
                        print(f"[FormFiller] Browser launched via: {channel}")
                    else:
                        browser = await p.chromium.launch(**launch_kwargs)
                        print("[FormFiller] Browser launched via: bundled Chromium")
                    break
                except Exception as e:
                    print(f"[FormFiller] Channel '{channel}' not available: {e}")
                    browser = None
            if not browser:
                raise RuntimeError("No browser could be launched.")

            # Signal ready the MOMENT the browser process is up.
            # /resume-form awaits this before calling event.set(),
            # so it can never race ahead of event.wait().
            if ready:
                ready.set()
                print("[FormFiller] READY - browser open, /resume-form may fire now.")

            ctx  = await browser.new_context(no_viewport=True)
            page = await ctx.new_page()

            # Bring the browser window to the foreground on Windows
            await page.bring_to_front()

            # Navigate to portal
            print("[FormFiller] Navigating to portal...")
            try:
                await page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=60000)
                await page.evaluate(
                    f"document.title = 'JOLLY-LLB - Applying: {scheme_id}'"
                )
                await page.bring_to_front()  # bring to front again after navigation
                print("[FormFiller] Portal loaded - OK")
            except Exception as e:
                print(f"[FormFiller] WARN: Portal load issue (browser still open): {e}")

            print("[FormFiller] PAUSED - waiting for /resume-form ...")

            # Browser stays open until event.set() is called
            await event.wait()

            print("[FormFiller] RESUMED - filling form now...")

            # Navigate to application form section (may already be visible)
            try:
                form_btn = page.locator("#go-to-form")
                if await form_btn.count() > 0:
                    await form_btn.click()
                # Wait for form section — generous timeout, non-fatal if missing
                await page.wait_for_selector("#application-form", timeout=8000)
            except Exception:
                pass  # form may already be visible; continue filling

            # ── 5. Fill fields ─────────────────────────────────────────
            field_map = SCHEME_FIELD_MAP.get(scheme_id, {})
            if not field_map:
                print(f"[FormFiller] ⚠  No field map for scheme '{scheme_id}', skipping fill.")

            for data_key, css_selector in field_map.items():
                value = user_data.get(data_key)
                if value is None:
                    continue
                await _safe_fill(page, css_selector, str(value), data_key)

            # Submit
            try:
                await page.locator("#submit-btn").click(timeout=5000)
                await page.wait_for_timeout(5000)  # hold on success page for 5s so user can see it
                print("[FormFiller] DONE - form submitted!")
            except Exception as e:
                print(f"[FormFiller] WARN: Submit button issue: {e}")

            await page.wait_for_timeout(3000)  # extra pause before browser closes

            await browser.close()

        if on_done:
            on_done()

    except Exception as e:
        print(f"[FormFiller] ERROR: {e}")
        try:
            if browser:
                await browser.close()
        except Exception:
            pass
        if on_error:
            on_error(str(e))
