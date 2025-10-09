# ActuVerse — Scraper (Python)

This repository contains a modular Python scraper designed to fetch news articles from multiple sources
and send them to a backend API (Symfony) for ingestion. It's intentionally simple and pluggable so you can
add more site scrapers under `sites/`.

## Quick start (local)

1. Create a virtualenv and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and edit `API_URL` if needed:
   ```bash
   cp .env.example .env
   ```

3. Run the scraper (dry-run prints to console, does not call the API):
   ```bash
   python main.py --dry-run
   ```

4. To post results to your backend API:
   ```bash
   export API_URL=http://localhost:8000/api/scraper/ingest
   python main.py
   ```

## Docker (simple)
A Dockerfile is included for the scraper. You can build and run with Docker:
```bash
docker build -t actuverse-scraper:latest .
docker run --rm -e API_URL=http://host.docker.internal:8000/api/scraper/ingest actuverse-scraper:latest
```

## How it works
- Each site scraper is a module inside `sites/` and exports a `scrape()` function that returns a list of article dicts.
- `main.py` orchestrates scrapers, deduplicates by URL, and calls `utils/save.py` to POST to the API.
- `utils/fetch.py` centralises HTTP requests (session + retries).
- Adjust selectors in each site module according to the site's HTML structure.

## Notes
- This environment cannot run live web requests here; you must run the scraper locally or in your environment.
- For JS-heavy sites, consider integrating Playwright or using `scrapy-playwright`.
