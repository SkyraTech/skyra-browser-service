# Skyra Browser Service

Playwright-powered browser automation service for visual analysis, scraping, and testing.

## Prerequisites
- Python 3.10+
- Playwright browser binaries

## Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate venv and install dependencies:
   ```bash
   venv\Scripts\activate
   pip install -r requirements.txt
   playwright install
   ```
3. Run the service:
   ```bash
   uvicorn main:app --port 8004
   ```
