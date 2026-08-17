"""
Skyra Browser Service — Phase 2B
==================================
A lightweight FastAPI service that exposes Playwright browser automation
over HTTP. Jarvis calls this service to browse the web, extract content,
fill forms, click elements, and take screenshots.

Port: 8004
"""

import asyncio
import base64
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger


# ── Global browser state ───────────────────────────────────────────────────
_playwright = None
_browser = None
_context = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start Playwright on startup, close on shutdown."""
    global _playwright, _browser, _context
    try:
        from playwright.async_api import async_playwright
        logger.info("🌐 Browser Service: Starting Playwright...")
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=True,          # Run headless for background tasks
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        _context = await _browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        logger.info("🌐 Browser Service: Playwright ready ✅")
    except Exception as e:
        logger.error(f"❌ Browser Service: Failed to start Playwright: {e}")
        logger.warning("  Run: playwright install chromium")

    yield

    # Cleanup
    if _context:
        await _context.close()
    if _browser:
        await _browser.close()
    if _playwright:
        await _playwright.stop()
    logger.info("🌐 Browser Service: Shut down cleanly")


app = FastAPI(
    title="Skyra Browser Service",
    description="Playwright browser automation for Jarvis",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request/Response Models ────────────────────────────────────────────────

class BrowseRequest(BaseModel):
    url: str
    wait_for: Optional[str] = None    # CSS selector to wait for

class ClickRequest(BaseModel):
    url: Optional[str] = None         # Navigate first if provided
    selector: str                     # CSS selector or text to click

class TypeRequest(BaseModel):
    selector: str
    text: str
    press_enter: bool = False

class ExtractRequest(BaseModel):
    url: str
    selector: Optional[str] = None    # Extract specific element, or full page

class SearchRequest(BaseModel):
    query: str
    engine: str = "google"            # google, bing, duckduckgo


# ── Helpers ────────────────────────────────────────────────────────────────

def _check_browser():
    if not _context:
        raise HTTPException(status_code=503, detail="Browser not initialized")


async def _get_page():
    """Get or create a page in the shared browser context."""
    _check_browser()
    pages = _context.pages
    if pages:
        return pages[-1]
    return await _context.new_page()


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "browser": _browser is not None}


@app.post("/browse")
async def browse(req: BrowseRequest):
    """
    Navigate to a URL and return the page title + main text content.
    This is the primary 'read a web page' endpoint for Jarvis.
    """
    _check_browser()
    try:
        page = await _get_page()
        logger.info(f"🌐 Browsing: {req.url}")
        await page.goto(req.url, wait_until="domcontentloaded", timeout=30000)

        if req.wait_for:
            await page.wait_for_selector(req.wait_for, timeout=10000)

        title = await page.title()

        # Extract clean readable text (strip scripts, styles, nav noise)
        text = await page.evaluate("""() => {
            const selectors = ['article', 'main', '.content', '#content', 'body'];
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el) {
                    // Remove script and style tags
                    el.querySelectorAll('script, style, nav, header, footer').forEach(e => e.remove());
                    const text = el.innerText;
                    if (text && text.length > 200) return text.slice(0, 5000);
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
        return {"success": False, "error": str(e)}


@app.post("/search")
async def search_web(req: SearchRequest):
    """
    Perform a web search and return the top results.
    """
    _check_browser()
    try:
        engines = {
            "google": f"https://www.google.com/search?q={req.query.replace(' ', '+')}",
            "bing": f"https://www.bing.com/search?q={req.query.replace(' ', '+')}",
            "duckduckgo": f"https://duckduckgo.com/?q={req.query.replace(' ', '+')}",
        }
        url = engines.get(req.engine, engines["google"])

        page = await _get_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # Extract search result snippets
        results = await page.evaluate("""() => {
            const items = [];
            // Google results
            document.querySelectorAll('div.g, div[data-sokoban-container]').forEach(el => {
                const title = el.querySelector('h3')?.innerText;
                const link = el.querySelector('a')?.href;
                const snippet = el.querySelector('div[data-sncf], span[data-ved]')?.innerText
                             || el.querySelector('.VwiC3b, .IsZvec')?.innerText;
                if (title && link) items.push({ title, link, snippet: snippet || '' });
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
        return {"success": False, "error": str(e)}


@app.post("/extract")
async def extract_content(req: ExtractRequest):
    """
    Navigate to URL and extract specific element content or full page text.
    """
    _check_browser()
    try:
        page = await _get_page()
        await page.goto(req.url, wait_until="domcontentloaded", timeout=30000)

        if req.selector:
            el = page.locator(req.selector).first
            content = await el.inner_text()
        else:
            content = await page.evaluate("() => document.body.innerText.slice(0, 8000)")

        return {"success": True, "content": content.strip()}
    except Exception as e:
        logger.error(f"❌ Extract error: {e}")
        return {"success": False, "error": str(e)}


@app.post("/click")
async def click_element(req: ClickRequest):
    """
    Click an element on the current page (or navigate first).
    """
    _check_browser()
    try:
        page = await _get_page()
        if req.url:
            await page.goto(req.url, wait_until="domcontentloaded")

        await page.click(req.selector, timeout=10000)
        await page.wait_for_load_state("domcontentloaded")
        title = await page.title()

        return {"success": True, "page_title": title, "current_url": page.url}
    except Exception as e:
        logger.error(f"❌ Click error: {e}")
        return {"success": False, "error": str(e)}


@app.post("/type")
async def type_text(req: TypeRequest):
    """
    Type text into an input field on the current page.
    """
    _check_browser()
    try:
        page = await _get_page()
        await page.fill(req.selector, req.text)
        if req.press_enter:
            await page.press(req.selector, "Enter")
            await page.wait_for_load_state("domcontentloaded")

        return {"success": True, "typed": req.text}
    except Exception as e:
        logger.error(f"❌ Type error: {e}")
        return {"success": False, "error": str(e)}


@app.post("/screenshot")
async def take_screenshot():
    """
    Take a screenshot of the current browser page.
    Returns base64-encoded PNG.
    """
    _check_browser()
    try:
        page = await _get_page()
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
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    logger.info("🌐 Starting Skyra Browser Service on port 8004...")
    uvicorn.run("main:app", host="127.0.0.1", port=8004, reload=False)
