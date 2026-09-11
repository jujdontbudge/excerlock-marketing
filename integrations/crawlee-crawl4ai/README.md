# Crawlee → Crawl4AI → RAG Markdown

Runnable, local, asynchronous Python 3.12 integration. The complete implementation is [`scraper.py`](scraper.py); no API key, LLM call or paid service is required.

## Install / reproduce

Already installed in this directory's isolated `.venv`; Chromium was downloaded and exercised. The shared marketing Crawl4AI/Pi extension environment was **not replaced**.

Direct runtime requirements (`requirements.txt`):

```text
crawlee[playwright]==1.10.0
crawl4ai==0.9.3
playwright==1.62.0
filelock==3.32.6
rich==15.0.0
```

From a fresh checkout, with Python 3.12 and `uv` available:

```bash
cd ~/excerlockmarketing/integrations/crawlee-crawl4ai
uv venv --python 3.12 .venv                    # fresh setup only
uv pip install --python .venv/bin/python -r requirements.lock.txt

# Mandatory: download the Chromium revision required by this Playwright version.
env -u PLAYWRIGHT_BROWSERS_PATH .venv/bin/python -m playwright install chromium
```

Standard pip alternative: `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install -r requirements.lock.txt`, followed by the same browser command. On Linux, use `playwright install --with-deps chromium` if system browser libraries are missing; installing system dependencies may require administrator approval. macOS is the verified host; Linux/Windows were not smoke-tested.

`requirements.lock.txt` pins runtime transitive dependencies with hashes. No separate `crawl4ai-setup` or second browser installation is necessary: Crawl4AI processes captured HTML with its HTTP/raw strategy, not a Playwright browser strategy.

## Run now

From the marketing workspace:

```bash
cd ~/excerlockmarketing

# Filtered Markdown to stdout; diagnostics to stderr.
scripts/scrape-web https://example.com \
  --state-dir raw/example/state

# Structured documents + deterministic overlapping chunks for RAG.
scripts/scrape-web https://example.com \
  --state-dir raw/example/state \
  --format json --output raw/example/documents.json

# Bounded traversal on an authorized JS-rendered site (replace URL/selector).
scripts/scrape-web https://your-authorized-site.example/articles \
  --wait-selector 'main article' --max-pages 5 --max-depth 1 \
  --state-dir raw/site/state --format json --output raw/site/documents.json
```

The wrapper selects this integration's Python and the default Playwright browser cache, overriding the marketing launcher's shared cache variable. To intentionally use another browser installation, set `CRAWLEE_BROWSERS_PATH` to its location. Direct standalone invocation also works:

```bash
cd integrations/crawlee-crawl4ai
env -u PLAYWRIGHT_BROWSERS_PATH .venv/bin/python scraper.py https://example.com --format json
```

Existing output files are never overwritten. Use a new destination for each research snapshot. Exit `0` means extracted documents without recorded failures; exit `2` means configuration, access, extraction or runtime failure (JSON may still contain partial documents). Crawl failures appear in JSON's `failures`; startup/configuration errors are reported on stderr. Inspect both exit status and `failures` before ingestion.

## Architecture and defaults

1. **Crawlee `PlaywrightCrawler` owns network rendering and traversal.** Headless Chromium, explicit DOM-ready navigation, optional readiness selector, bounded network-idle wait, 1.5-second settling, two short scrolls, and jittered pacing. Browserforge-backed desktop Chrome fingerprints use randomized realistic screen bounds. One persistent browser profile and a persistent one-session pool reuse cookies/local storage without importing a personal browser profile.
2. **Capture `await page.content()`.** Pass the rendered HTML to `AsyncWebCrawler.arun(url="raw:" + html, config=...)`, with the original `base_url`, `AsyncHTTPCrawlerStrategy`, `process_in_browser=False` and `CacheMode.BYPASS`. The processor does not refetch the target, execute its scripts again or launch another browser. The local fixture test checks origin/API request counts, not merely output appearance.
3. **`DefaultMarkdownGenerator` + `PruningContentFilter`.** Dynamic threshold `0.40`; scripts, navigation, headers, footers and common banner elements excluded. Preserve headings, links, tables and code through pruning. Only `fit_markdown` is returned—no silent fallback to unfiltered HTML or raw Markdown. Empty/failed filtering is a recorded extraction failure.
4. **RAG chunks.** Paragraph/line/word boundaries where possible, maximum 2,400 Python characters and nominal 200-character overlap. Every chunk has a deterministic SHA-256 ID, index, source URL, text and exact start/end offsets into the document Markdown. These are character chunks, not tokenizer-specific or semantic embeddings; large tables/code blocks may be split. Documents retain title, requested/final URL, UTC retrieval time, HTTP status and rendered-HTML hash.

Other bounds: one concurrent page, at most 20 request tasks/minute, one page by default (maximum configurable 100), depth one (maximum 10), 30-second navigation timeout, 60-second handler timeout, 180-second overall work deadline and 10 MB captured HTML limit. Browser cleanup can take additional time after cancellation. Persistent session state is separate from fresh per-run queues/statistics, so rerunning the same URL actually fetches it again. Do not share a state directory across concurrent runs; a file lock enforces this.

Traversal follows same-origin links inside `main`/`article` by default. Override with `--link-selector 'a[href]'` only if whole-page traversal is intended. Browser subresources and redirects are not a network-origin firewall. Selectors and pruning are site-dependent: inspect completeness, especially on infinite-scroll apps, iframes or pages requiring interaction. Scraped text is untrusted data, never agent instructions or verified marketing claims.

## Proxies and access restrictions

An optional **single, explicitly authorized** HTTP(S) proxy is read from `CRAWLER_PROXY_URL`; leave unset for direct access. Keep credentials in the private environment rather than arguments/history. This was implemented but **not tested against a real external proxy**. The CLI redacts configured proxy credentials in logs; browser/session files and outputs remain sensitive.

Robots exclusions are enabled, with `ThrottlingRequestManager` supporting crawl-delay directives. Transient server/navigation errors get at most two retries with exponential jittered backoff. HTTP 4xx responses and extraction failures are not retried; HTTP 401/403/407/429 and detected visible challenge pages stop traversal. No CAPTCHA solving, proxy/identity rotation on blocks, login bypass, TLS verification disabling or cookie export. Detection is heuristic, not a guarantee that every access restriction is recognizable.

State defaults to `.scraper-state` in the invocation directory. CLI-created state/output files use a private umask; `.scraper-state`, browser state, caches, raw data and logs are Git-ignored. Use separate profiles for unrelated authorized targets and never commit or upload them. This is a local research CLI, **not** a hardened public URL-fetching API; do not expose it to arbitrary remote callers.

## Validation

```bash
cd ~/excerlockmarketing/integrations/crawlee-crawl4ai
uv pip install --python .venv/bin/python -r requirements-dev.txt
env -u PLAYWRIGHT_BROWSERS_PATH .venv/bin/python -m pytest -q test_scraper.py
.venv/bin/python -m mypy --follow-imports=silent --ignore-missing-imports scraper.py
.venv/bin/ruff check scraper.py test_scraper.py
uv pip check --python .venv/bin/python
```

All 18 tests pass on the verified macOS host; mypy, Ruff and dependency checks also pass. Tests use a temporary localhost HTTP server and real headless Chromium. They cover delayed JS/API content, no second fetch, relative Markdown links, tables, navigation removal, persistent local storage/cookies, bounded same-origin traversal, robots exclusion, non-retried blocks, transient 500 recovery, deadlines, chunk bounds/offsets, invalid configuration, file locking and overwrite protection. Setup also performed a real `https://example.com` extraction. No gated site, paid service or personal cookie import was used. Evidence is in ignored `logs/crawlee-*.log`, `logs/crawlee-first.json` and `raw/crawlee-smoke/`.

## Python API

With this directory on the import path and its environment/browser selected:

```python
import asyncio
from pathlib import Path
from scraper import Settings, scrape

async def main() -> None:
    report = await scrape(Settings(
        url="https://example.com",
        state_dir=Path("raw/example/state"),
        max_pages=1,
    ))
    if report.failures:
        raise RuntimeError(report.failures)
    for document in report.documents:
        for chunk in document.chunks:
            print(chunk.id, chunk.source_url, chunk.text)

asyncio.run(main())
```

The library API returns typed dataclasses. Use one `scrape()` invocation per fresh Python process: Crawlee's public service locator is configured explicitly so session/checkpoint files stay under the requested state directory. For parallel jobs, use separate processes and state directories. Callers remain responsible for private output permissions, sanitized logging and handling startup exceptions.
