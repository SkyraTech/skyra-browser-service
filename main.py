"""
Skyra Browser Service
=====================
FastAPI microservice exposing Playwright browser automation.
Supports stealth anti-detection measures and request-scoped isolated tab navigation.

Port: 8004
"""

import asyncio
import base64
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from loguru import logger


# ── Global browser state ───────────────────────────────────────────────────
_playwright = None
_browser = None
_context = None
_active_page = None  # Persistent page for stateful clicks, typing, and screenshots


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start Playwright on startup with stealth options, close on shutdown."""
    global _playwright, _browser, _context
    try:
        from playwright.async_api import async_playwright
        logger.info("🌐 Browser Service: Starting Playwright...")
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        _context = await _browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        # Neutralize navigator.webdriver stealth init script
        await _context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        logger.info("🌐 Browser Service: Playwright Context ready with stealth configurations ✅")
    except Exception as e:
        logger.error(f"❌ Browser Service: Failed to start Playwright: {e}")

    yield

    # Cleanup active tab page
    global _active_page
    if _active_page:
        try:
            await _active_page.close()
        except Exception:
            pass
    # Cleanup context and browser
    if _context:
        await _context.close()
    if _browser:
        await _browser.close()
    if _playwright:
        await _playwright.stop()
    logger.info("🌐 Browser Service: Shut down cleanly")


app = FastAPI(
    title="Skyra Browser Service",
    description="Stealth Playwright browser automation for Jarvis",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request/Response Models ────────────────────────────────────────────────

class BrowseRequest(BaseModel):
    url: str = Field(..., description="Target webpage URL to navigate to")
    wait_for: Optional[str] = Field(None, description="Optional CSS selector to wait for")

class ClickRequest(BaseModel):
    url: Optional[str] = Field(None, description="Optional URL to navigate to first")
    selector: str = Field(..., description="CSS selector of element to click")

class TypeRequest(BaseModel):
    selector: str = Field(..., description="CSS selector of target input element")
    text: str = Field(..., description="Text content to input")
    press_enter: bool = Field(False, description="True to simulate Enter keypress after filling")

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query string")
    engine: str = Field("google", description="Target search engine: google, bing, duckduckgo")


# ── Helpers ────────────────────────────────────────────────────────────────

def _check_browser():
    if not _context:
        raise HTTPException(status_code=503, detail="Browser not initialized or offline")


async def _get_active_page():
    """Retrieve or spawn the persistent active page context for stateful user interaction tools."""
    global _active_page
    _check_browser()
    if _active_page is None or _active_page.is_closed():
        _active_page = await _context.new_page()
    return _active_page


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "skyra-browser-service",
        "browser": _browser is not None,
        "active_tab": _active_page is not None and not _active_page.is_closed()
    }


@app.post("/browse")
async def browse(req: BrowseRequest):
    """
    Stateless webpage reader: opens a fresh page, navigates, extracts readable content,
    and closes the page inside a finally block to avoid memory leaks.
    """
    _check_browser()
    page = await _context.new_page()
    try:
        logger.info(f"🌐 Browsing: {req.url}")
        await page.goto(req.url, wait_until="domcontentloaded", timeout=30000)

        if req.wait_for:
            await page.wait_for_selector(req.wait_for, timeout=10000)

        title = await page.title()

        # Clean read of inner body text (excluding script tags, headers/footers)
        text = await page.evaluate("""() => {
            const selectors = ['article', 'main', '.content', '#content', 'body'];
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el) {
                    const clone = el.cloneNode(true);
                    clone.querySelectorAll('script, style, nav, header, footer').forEach(e => e.remove());
                    const txt = clone.innerText;
                    if (txt && txt.length > 200) return txt.slice(0, 5000);
                }
            }
            return document.body.innerText.slice(0, 5000);
        }""")

        return {
            "success": True,
            "url": page.url,
            "title": title,
            "content": text.strip(),
        }
    except Exception as e:
        logger.error(f"❌ Browse error: {e}")
        raise HTTPException(status_code=500, detail=f"Navigation failed: {str(e)}")
    finally:
        await page.close()


@app.post("/search")
async def search_web(req: SearchRequest):
    """
    Queries Google Search with robust selector fallbacks, returns title/link/snippet matching,
    and closes pages immediately.
    """
    _check_browser()
    page = await _context.new_page()
    try:
        query_encoded = req.query.replace(' ', '+')
        url = f"https://www.google.com/search?q={query_encoded}"
        
        logger.info(f"🌐 Querying SERP: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # Parse SERP elements with robust fallbacks
        results = await page.evaluate("""() => {
            const items = [];
            document.querySelectorAll('div.g, div[data-sokoban-container], div.kvH3rc, div.Z26q7c').forEach(el => {
                const titleEl = el.querySelector('h3');
                const linkEl = el.querySelector('a');
                if (titleEl && linkEl) {
                    const title = titleEl.innerText;
                    const link = linkEl.href;
                    const snippetEl = el.querySelector('div[data-sncf], span[data-ved], .VwiC3b, .IsZvec, .MUFIy, .Yy30fd');
                    const snippet = snippetEl ? snippetEl.innerText : '';
                    items.push({ title, link, snippet });
                }
            });
            return items.slice(0, 8);
        }""")

        return {
            "success": True,
            "query": req.query,
            "results": results,
        }
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search query failed: {str(e)}")
    finally:
        await page.close()


@app.post("/click")
async def click_element(req: ClickRequest):
    """
    Executes a click against selector on the active browser tab page.
    """
    _check_browser()
    try:
        page = await _get_active_page()
        if req.url:
            await page.goto(req.url, wait_until="domcontentloaded", timeout=30000)

        await page.wait_for_selector(req.selector, timeout=10000)
        await page.click(req.selector, timeout=10000)
        await page.wait_for_load_state("domcontentloaded")
        title = await page.title()

        return {
            "success": True,
            "page_title": title,
            "current_url": page.url
        }
    except Exception as e:
        logger.error(f"❌ Click error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to click selector: {str(e)}")


@app.post("/type")
async def type_text(req: TypeRequest):
    """
    Fills text into target form element on the active page context.
    """
    _check_browser()
    try:
        page = await _get_active_page()
        await page.wait_for_selector(req.selector, timeout=10000)
        await page.fill(req.selector, req.text)
        if req.press_enter:
            await page.press(req.selector, "Enter")
            await page.wait_for_load_state("domcontentloaded")

        return {
            "success": True,
            "typed": req.text
        }
    except Exception as e:
        logger.error(f"❌ Type error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to input text: {str(e)}")


@app.post("/screenshot")
async def take_screenshot():
    """
    Captures base64 viewport snapshot of the active page tab.
    """
    _check_browser()
    try:
        page = await _get_active_page()
        screenshot_bytes = await page.screenshot(full_page=False)
        encoded = base64.b64encode(screenshot_bytes).decode("utf-8")
        return {
            "success": True,
            "format": "png",
            "base64": encoded,
            "current_url": page.url,
        }
    except Exception as e:
        logger.error(f"❌ Screenshot error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to render screenshot: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    logger.info("🌐 Starting Skyra Browser Service on port 8004...")
    uvicorn.run("main:app", host="127.0.0.1", port=8004, reload=False)
