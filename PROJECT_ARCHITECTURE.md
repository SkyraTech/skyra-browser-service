# skyra-browser-service — Project Architecture & Design Specification (PAD)

## 1. Executive Summary & Core Responsibilities
`skyra-browser-service` is a specialized Playwright-based browser automation microservice. It exposes HTTP REST endpoints that enable `skyra-jarvis` to interact with standard web sites, execute searches, click buttons, input forms, extract readable content, and take screenshot captures of active web sessions.

### Service SLAs
* **Browsing Page Navigation**: Load pages and extract raw text within 5.0 seconds.
* **Element Interactivity**: Execute clicks and inputs within 1.0 second.
* **Screenshot Rendering**: Capture and base64-encode viewports within 1.5 seconds.

---

## 2. High-Level Architecture & Lifecycle Diagrams

```text
  Client (Jarvis Tool Call)
              │
              ▼ [HTTP POST]
     FastAPI Endpoints (main.py)
              │
              ▼ [Request-Scoped Page (new_page)]
     Isolated Playwright Tab Page
              │
              ├─► Evades Bot Detection (Stealth Scripts, Custom UA)
              ▼
   Chromium Browser Context (Singleton)
```

### Component Interaction Matrix

| Source Component | Target Component | Protocol | Payload Format | Description |
| :--- | :--- | :--- | :--- | :--- |
| `skyra-jarvis` | `/browse` | HTTP POST | JSON | Navigates to target URL and returns clean readable body text |
| `skyra-jarvis` | `/search` | HTTP POST | JSON | Submits search query and returns parsed Google SERP item list |
| `skyra-jarvis` | `/click` | HTTP POST | JSON | Executes click on target selector inside active page context |
| `skyra-jarvis` | `/type` | HTTP POST | JSON | Fills text inside input/textarea selectors in page context |
| `skyra-jarvis` | `/screenshot` | HTTP POST | JSON | Captures base64 PNG viewport of the active page tab |

---

## 3. Directory Structure & Code Taxonomy
```text
apps/skyra-browser-service/
├── main.py                  ← FastAPI entry point and Playwright controllers
├── requirements.txt         ← python dependencies (fastapi, playwright, loguru, uvicorn)
├── .gitignore               ← venv and caching rules
├── .env                     ← Local service settings
└── .env.example             ← Env template
```

### Lifecycle Scopes
* **Lifespan Context Manager**: Playwright `async_playwright` and Chromium `browser` instances are initialized as global singletons on FastAPI startup, and closed cleanly on shutdown.
* **Request-Scoped Browser Pages**: To prevent memory leaks, every `/browse`, `/search`, `/click`, `/type`, and `/screenshot` endpoint opens a `new_page()` off the global `BrowserContext` and ensures it is closed in a `finally` block.

---

## 4. Technical Specs & Feature Deep-Dive

### Stealth & Anti-Detection
The microservice executes stealth measures on Chromium initialization to evade bot-detection systems:
1. **Automation Control Disabling**: Launches Chromium with `--disable-blink-features=AutomationControlled` argument.
2. **Navigator.webdriver Neutralization**: Injects an initialization script into every page:
   `Object.defineProperty(navigator, 'webdriver', {get: () => undefined})`
3. **User-Agent Masquerading**: Configures the shared context with a standard user-agent string simulating active Desktop users.

### API Endpoint Schemas

#### A. `/browse` (POST)
Navigates to URL, waits for load state, and parses cleaned inner text.
* **Request Schema**:
  ```json
  {
    "url": "https://example.com",
    "wait_for": "div.content-wrapper"
  }
  ```
* **Response Schema**:
  ```json
  {
    "success": true,
    "url": "https://example.com/",
    "title": "Example Domain",
    "content": "Clean page text content..."
  }
  ```

#### B. `/search` (POST)
Queries Google Search using robust fallbacks for parsing elements (headers, snippets, links).
* **Request Schema**:
  ```json
  {
    "query": "Skyra Tech",
    "engine": "google"
  }
  ```
* **Response Schema**:
  ```json
  {
    "success": true,
    "query": "Skyra Tech",
    "results": [
      {
        "title": "Skyra Tech Ecosystem",
        "link": "https://github.com/SkyraTech",
        "snippet": "Distributed enterprise AI automation suites..."
      }
    ]
  }
  ```

#### C. `/click` (POST)
Simulates element clicks inside the active page session.
* **Request Schema**:
  ```json
  {
    "url": "https://example.com",
    "selector": "button#submit"
  }
  ```
* **Response Schema**:
  ```json
  {
    "success": true,
    "page_title": "Example Domain",
    "current_url": "https://example.com/submit"
  }
  ```

#### D. `/type` (POST)
Simulates input text keystrokes inside target form inputs.
* **Request Schema**:
  ```json
  {
    "selector": "input[name='q']",
    "text": "Jarvis assistant",
    "press_enter": true
  }
  ```
* **Response Schema**:
  ```json
  {
    "success": true,
    "typed": "Jarvis assistant"
  }
  ```

#### E. `/screenshot` (POST)
Captures and base64-encodes the active Chromium tab viewport.
* **Response Schema**:
  ```json
  {
    "success": true,
    "format": "png",
    "base64": "iVBORw0KGgoAAAANSUhEUg...",
    "current_url": "https://example.com"
  }
  ```

---

## 5. Security, Environment & Configuration
* **Port Binding**: Port `8004`. Exposes interface to loopback `127.0.0.1` only.
* **CORS Settings**: Restricts cross-origin requests specifically to `http://127.0.0.1:8000`.
* **Chromium Args**: Launched with `--no-sandbox`, `--disable-dev-shm-usage`, and `--disable-blink-features=AutomationControlled` to prevent sandbox failures and detection.

---

## 6. Resilience, Error Handling & Recovery Strategies
* **Browser Health Check**: `/health` queries the initialization state of Chromium.
* **Request-Scoped Isolation**: Pages are instantiated per request and closed in `finally` statements to reclaim memory.
* **Navigation Timeout Bounds**: Navigation limits are set to 30.0 seconds, and element selectors to 10.0 seconds. Exceptions are caught and returned as clean JSON error states to Jarvis.

---

## 7. Ecosystem Integration & Dependencies
Dependent upon by `skyra-jarvis` to execute text extractions and submit forms on target sites. Exposes REST API over loopback port `8004`.
