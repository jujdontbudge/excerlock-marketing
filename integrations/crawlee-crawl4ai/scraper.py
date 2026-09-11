#!/usr/bin/env python3
"""Crawlee renders/traverses; Crawl4AI converts captured HTML locally to RAG Markdown.

No CAPTCHA solving, stealth patches, proxy rotation or block-triggered retries.
Only crawler-owned cookies/local storage are persisted. Never use a personal browser profile.
Use one scrape() invocation per Python process and one process per state directory. Python 3.12+.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import math
import os
import random
import re
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from functools import partial
from pathlib import Path
from typing import Literal
from urllib.parse import unquote, urlsplit
from uuid import uuid4

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from crawl4ai.async_crawler_strategy import AsyncHTTPCrawlerStrategy
from crawl4ai.async_logger import AsyncLogger
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawlee import ConcurrencySettings, service_locator
from crawlee.configuration import Configuration
from crawlee.crawlers import (
    BasicCrawlingContext,
    PlaywrightCrawler,
    PlaywrightCrawlingContext,
    PlaywrightPostNavCrawlingContext,
    PlaywrightPreNavCrawlingContext,
)
from crawlee.errors import HttpStatusCodeError
from crawlee.events import LocalEventManager
from crawlee.fingerprint_suite import (
    DefaultFingerprintGenerator,
    HeaderGeneratorOptions,
    ScreenOptions,
)
from crawlee.proxy_configuration import ProxyConfiguration
from crawlee.request_loaders import ThrottlingRequestManager
from crawlee.sessions import SessionPool
from crawlee.statistics import Statistics
from crawlee.storage_clients import FileSystemStorageClient
from crawlee.storages import RequestQueue
from filelock import FileLock
from filelock import Timeout as FileLockTimeout
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from rich.console import Console

LOG = logging.getLogger("marketing.scraper")
BLOCKED_STATUSES = frozenset({401, 403, 407, 429, 451})
BLOCKED_TITLES = re.compile(
    r"^(?:just a moment[.!…]*|access denied|attention required[! ]*(?:\| cloudflare)?|"
    r"verify (?:that )?you are human|security verification|captcha)$", re.IGNORECASE,
)
CHALLENGE_SELECTORS = (
    "#challenge-running", "#challenge-stage", "form#challenge-form",
    'iframe[src*="challenges.cloudflare.com"]', 'iframe[src*="hcaptcha.com/captcha"]',
    'iframe[src*="recaptcha/api2/bframe"]',
)


class ScrapeError(Exception):
    """Recoverable pipeline error with a safe, non-secret message."""


class BlockedRequest(ScrapeError):
    """Access restriction detected; do not retry or rotate identities."""


class ExtractionError(ScrapeError):
    """HTML could not produce meaningful filtered Markdown."""


@dataclass(frozen=True, slots=True)
class Settings:
    url: str
    state_dir: Path = Path(".scraper-state")
    max_pages: int = 1
    max_depth: int = 1
    wait_selector: str = "body"
    link_selector: str = "main a[href], article a[href]"
    navigation_timeout: float = 30.0
    handler_timeout: float = 60.0
    total_timeout: float = 180.0
    settle_seconds: float = 1.5
    scroll_steps: int = 2
    prune_threshold: float = 0.40
    chunk_chars: int = 2400
    overlap_chars: int = 200
    max_html_bytes: int = 10_000_000
    headless: bool = True
    proxy_url: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        validate_url(self.url)
        if not 1 <= self.max_pages <= 100 or not 0 <= self.max_depth <= 10:
            raise ValueError("max_pages must be 1..100; max_depth must be 0..10")
        if not self.wait_selector.strip() or not self.link_selector.strip():
            raise ValueError("wait_selector and link_selector cannot be empty")
        if not all(math.isfinite(value) for value in (
            self.navigation_timeout, self.handler_timeout, self.total_timeout,
            self.settle_seconds, self.prune_threshold,
        )):
            raise ValueError("Numeric timing and pruning settings must be finite")
        if min(self.navigation_timeout, self.handler_timeout, self.total_timeout) <= 0:
            raise ValueError("Timeouts must be positive")
        if self.settle_seconds < 0 or not 0 <= self.scroll_steps <= 10:
            raise ValueError("settle_seconds must be nonnegative; scroll_steps must be 0..10")
        if not 0 < self.prune_threshold < 1:
            raise ValueError("prune_threshold must be between zero and one")
        if self.chunk_chars < 128 or not 0 <= self.overlap_chars < self.chunk_chars // 2:
            raise ValueError("chunk_chars must be >=128; overlap must be less than half the chunk size")
        if self.max_html_bytes < 1024:
            raise ValueError("max_html_bytes must be >=1024")
        if self.proxy_url:
            proxy = urlsplit(self.proxy_url)
            if proxy.scheme not in {"http", "https"} or not proxy.hostname:
                raise ValueError("CRAWLER_PROXY_URL must be an HTTP(S) proxy URL")


@dataclass(frozen=True, slots=True)
class Chunk:
    id: str
    index: int
    source_url: str
    start_char: int
    end_char: int
    text: str


@dataclass(frozen=True, slots=True)
class Document:
    requested_url: str
    url: str
    title: str
    retrieved_at: str
    status_code: int
    html_sha256: str
    markdown: str
    chunks: list[Chunk]


@dataclass(frozen=True, slots=True)
class Failure:
    url: str
    category: Literal["blocked", "request", "extraction", "timeout", "empty"]
    message: str


@dataclass(slots=True)
class CrawlReport:
    documents: list[Document] = field(default_factory=list)
    failures: list[Failure] = field(default_factory=list)


def validate_url(url: str) -> None:
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
        raise ValueError("Target must be an absolute HTTP(S) URL without embedded credentials")
    _ = parts.port  # Validate malformed/out-of-range ports before opening a browser.


def chunk_markdown(text: str, source_url: str, size: int, overlap: int) -> list[Chunk]:
    """Exact source slices, preferring paragraph/line/word boundaries; sizes are characters, not tokens.

    Long paragraphs, tables and code fences may span chunks. Full Markdown is always retained.
    Offsets allow deterministic reconstruction and citation without fabricated text.
    """
    if size < 128 or not 0 <= overlap < size // 2:
        raise ValueError("Invalid chunk size/overlap")
    chunks: list[Chunk] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            lower = start + size // 2
            for separator in ("\n\n", "\n", " "):
                boundary = text.rfind(separator, lower, end)
                if boundary >= lower:
                    end = boundary + len(separator)
                    break
        part = text[start:end]
        if part.strip():
            digest = hashlib.sha256(f"{source_url}\0{start}\0{part}".encode()).hexdigest()
            chunks.append(Chunk(digest, len(chunks), source_url, start, end, part))
        if end == len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks


async def reject_challenge(context: PlaywrightPostNavCrawlingContext | PlaywrightCrawlingContext) -> None:
    if context.response.status in BLOCKED_STATUSES:
        context.request.no_retry = True
        raise BlockedRequest(f"HTTP {context.response.status}; stopped without bypass")
    title = (await context.page.title()).strip()
    if BLOCKED_TITLES.fullmatch(title):
        context.request.no_retry = True
        raise BlockedRequest("Challenge/interstitial title detected; stopped without bypass")
    for selector in CHALLENGE_SELECTORS:
        if await context.page.locator(selector).first.is_visible():
            context.request.no_retry = True
            raise BlockedRequest("Visible challenge/CAPTCHA detected; stopped without bypass")


async def process_html(
    processor: AsyncWebCrawler, html: str, url: str, settings: Settings,
) -> str:
    """No target refetch: raw: + HTTP strategy parses the supplied HTML without running its scripts."""
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        base_url=url,
        process_in_browser=False,
        verbose=False,
        word_count_threshold=1,
        table_score_threshold=1,
        excluded_tags=["nav", "footer", "script", "style", "noscript", "form"],
        excluded_selector="body > header, [role='navigation'], [role='banner'], [role='contentinfo']",
        remove_forms=True,
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(
                threshold=settings.prune_threshold, threshold_type="dynamic", min_word_threshold=5,
                preserve_tags=["table", "pre", "a", "h1", "h2", "h3", "h4", "h5", "h6"],
            ),
            options={"ignore_links": False, "ignore_images": True, "body_width": 0},
        ),
    )
    result = await processor.arun(url="raw:" + html, config=config)
    if not result.success or result.markdown is None:
        # Do not print error_message: a third-party error can contain the entire raw HTML.
        raise ExtractionError("Crawl4AI raw HTML processing failed")
    markdown = (result.markdown.fit_markdown or "").strip()
    if not markdown or not result.markdown.fit_html:
        raise ExtractionError("Pruning returned no content; refine selector/threshold, don't treat this as success")
    return markdown


async def scrape(settings: Settings) -> CrawlReport:
    """Return typed documents/failures. No LLM API, paid inference or external extraction service is used."""
    report = CrawlReport()
    state = settings.state_dir.expanduser().resolve()
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    state.chmod(0o700)
    # OS-backed lock releases on crashes; prevents corrupting a shared browser profile.
    with FileLock(str(state / "pipeline.lock"), timeout=0):
        task = asyncio.create_task(_run(settings, state, report))
        try:
            done, _ = await asyncio.wait({task}, timeout=settings.total_timeout)
            if done:
                await task
            else:
                task.cancel()
                # Browser shutdown may wrap cancellation in an ExceptionGroup. Drain it and
                # preserve the deadline as the actual cause rather than reporting startup failure.
                await asyncio.gather(task, return_exceptions=True)
                report.failures.append(Failure(settings.url, "timeout", "Overall crawl deadline exceeded"))
        except BaseException:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
            raise
    if not report.documents and not report.failures:
        report.failures.append(Failure(settings.url, "empty", "No document extracted (possibly robots.txt exclusion)"))
    return report


async def _run(settings: Settings, state: Path, report: CrawlReport) -> None:
    quiet_logger = AsyncLogger(verbose=False, console=Console(file=sys.stderr))
    configuration = Configuration(storage_dir=str(state / "crawlee"), purge_on_start=False)
    storage_client = FileSystemStorageClient()
    event_manager = LocalEventManager()
    # SessionPool and request-manager checkpoints use Crawlee's public global locator.
    # Configure it before opening any storage so cookies cannot leak into ./storage.
    service_locator.set_configuration(configuration)
    service_locator.set_storage_client(storage_client)
    service_locator.set_event_manager(event_manager)
    # A fresh named queue prevents handled URLs from a previous run being silently skipped.
    # Browser/session storage is separate and survives request queue cleanup.
    queue = await RequestQueue.open(name=f"pages-{uuid4().hex}", configuration=configuration, storage_client=storage_client)
    throttler = ThrottlingRequestManager(
        queue,
        domains=[urlsplit(settings.url).hostname or ""],
        request_manager_opener=partial(RequestQueue.open, configuration=configuration, storage_client=storage_client),
    )
    # Use the non-browser raw strategy: Crawlee is the only renderer/network traversal engine.
    async with AsyncWebCrawler(
        crawler_strategy=AsyncHTTPCrawlerStrategy(logger=quiet_logger),
        config=BrowserConfig(verbose=False),
        logger=quiet_logger,
        base_directory=str(state / "crawl4ai"),
    ) as processor:
        crawler = PlaywrightCrawler(
            configuration=configuration,
            storage_client=storage_client,
            request_manager=throttler,
            statistics=Statistics.with_default_state(persistence_enabled=False),
            event_manager=event_manager,
            browser_type="chromium",
            headless=settings.headless,
            user_data_dir=state / "browser-profile",
            use_incognito_pages=False,
            browser_new_context_options={"ignore_https_errors": False, "accept_downloads": False},
            fingerprint_generator=DefaultFingerprintGenerator(
                header_options=HeaderGeneratorOptions(browsers=["chrome"], devices=["desktop"]),
                screen_options=ScreenOptions(min_width=1280, max_width=1920, min_height=720, max_height=1080),
            ),
            session_pool=SessionPool(max_pool_size=1, persistence_enabled=True),
            proxy_configuration=ProxyConfiguration(proxy_urls=[settings.proxy_url]),
            concurrency_settings=ConcurrencySettings(min_concurrency=1, max_concurrency=1, desired_concurrency=1, max_tasks_per_minute=20),
            max_requests_per_crawl=settings.max_pages,
            max_crawl_depth=settings.max_depth,
            max_request_retries=2,
            max_session_rotations=0,
            retry_on_blocked=False,
            respect_robots_txt_file=True,
            navigation_timeout=timedelta(seconds=settings.navigation_timeout),
            request_handler_timeout=timedelta(seconds=settings.handler_timeout),
            goto_options={"wait_until": "domcontentloaded"},
            configure_logging=False,
        )

        @crawler.pre_navigation_hook
        async def pace(_context: PlaywrightPreNavCrawlingContext) -> None:
            await asyncio.sleep(random.uniform(0.5, 1.2))

        @crawler.post_navigation_hook
        async def check_response(context: PlaywrightPostNavCrawlingContext) -> None:
            if 400 <= context.response.status < 500:
                context.request.no_retry = True
            await reject_challenge(context)

        @crawler.router.default_handler
        async def handle(context: PlaywrightCrawlingContext) -> None:
            await context.page.locator(settings.wait_selector).first.wait_for(
                state="visible", timeout=settings.navigation_timeout * 1000,
            )
            # networkidle alone hangs on streaming/analytics-heavy sites. Bound it, then settle.
            try:
                await context.page.wait_for_load_state("networkidle", timeout=3000)
            except PlaywrightTimeoutError:
                LOG.debug("Network did not become idle; using the explicit selector and bounded settle delay")
            await asyncio.sleep(settings.settle_seconds + random.uniform(0.0, 0.4))
            for _ in range(settings.scroll_steps):
                await context.page.mouse.wheel(0, random.randint(300, 650))
                await asyncio.sleep(random.uniform(0.25, 0.6))
            await reject_challenge(context)
            final_url = context.page.url
            validate_url(final_url)
            html = await context.page.content()
            encoded = html.encode("utf-8")
            if len(encoded) > settings.max_html_bytes:
                context.request.no_retry = True
                raise ExtractionError("Rendered HTML exceeds the configured byte limit")
            title = await context.page.title()
            try:
                markdown = await process_html(processor, html, final_url, settings)
            except ExtractionError:
                context.request.no_retry = True
                raise
            if len(report.documents) + 1 < settings.max_pages:
                await context.enqueue_links(selector=settings.link_selector, strategy="same-origin", limit=settings.max_pages - len(report.documents) - 1)
            report.documents.append(Document(
                requested_url=context.request.url,
                url=final_url,
                title=title,
                retrieved_at=datetime.now(timezone.utc).isoformat(),
                status_code=context.response.status,
                html_sha256=hashlib.sha256(encoded).hexdigest(),
                markdown=markdown,
                chunks=chunk_markdown(markdown, final_url, settings.chunk_chars, settings.overlap_chars),
            ))

        @crawler.error_handler
        async def on_error(context: BasicCrawlingContext, error: Exception) -> None:
            # Permanent failures and restrictions never trigger a new identity or proxy.
            if isinstance(error, (BlockedRequest, ExtractionError)) or (
                isinstance(error, HttpStatusCodeError) and 400 <= error.status_code < 500
            ):
                context.request.no_retry = True
            else:
                await asyncio.sleep(min(8.0, 2.0 ** context.request.retry_count) + random.uniform(0, 0.5))

        @crawler.failed_request_handler
        async def failed(context: BasicCrawlingContext, error: Exception) -> None:
            blocked = isinstance(error, BlockedRequest) or (
                isinstance(error, HttpStatusCodeError) and error.status_code in BLOCKED_STATUSES
            )
            category: Literal["blocked", "request", "extraction"] = (
                "blocked" if blocked else "extraction" if isinstance(error, ExtractionError) else "request"
            )
            message = str(error) if isinstance(error, ScrapeError) else type(error).__name__
            report.failures.append(Failure(context.request.url, category, message))
            if blocked:
                crawler.stop("Access restriction encountered; no bypass, rotation or further traversal")

        try:
            await crawler.run([settings.url], purge_request_queue=False)
        finally:
            await throttler.drop()


class SecretFilter(logging.Filter):
    def __init__(self, proxy_url: str | None) -> None:
        super().__init__()
        self.secrets = [proxy_url] if proxy_url else []
        if proxy_url and urlsplit(proxy_url).password:
            self.secrets.append(unquote(urlsplit(proxy_url).password or ""))

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        for secret in self.secrets:
            if secret:
                message = message.replace(secret, "[REDACTED]")
        record.msg, record.args = message, ()
        # Do not leak proxy credentials/HTML through a third-party traceback.
        if self.secrets and record.exc_info:
            record.exc_info = None
            record.exc_text = None
        return True


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--state-dir", type=Path, default=Path(".scraper-state"))
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--max-depth", type=int, default=1)
    parser.add_argument("--wait-selector", default="body")
    parser.add_argument("--link-selector", default="main a[href], article a[href]")
    parser.add_argument("--settle-seconds", type=float, default=1.5)
    parser.add_argument("--scroll-steps", type=int, default=2)
    parser.add_argument("--navigation-timeout", type=float, default=30.0)
    parser.add_argument("--handler-timeout", type=float, default=60.0)
    parser.add_argument("--total-timeout", type=float, default=180.0)
    parser.add_argument("--prune-threshold", type=float, default=0.40)
    parser.add_argument("--chunk-chars", type=int, default=2400)
    parser.add_argument("--overlap-chars", type=int, default=200)
    parser.add_argument("--max-html-bytes", type=int, default=10_000_000)
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", type=Path, help="New output file; refuses to overwrite")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    # Private browser/session state and output artifacts; no personal profile import.
    os.umask(0o077)
    handler = logging.StreamHandler(sys.stderr)
    handler.addFilter(SecretFilter(os.environ.get("CRAWLER_PROXY_URL")))
    logging.basicConfig(level=logging.WARNING, handlers=[handler], force=True)
    output_file: Path | None = args.output
    if output_file and output_file.exists():
        LOG.error("Output already exists; choose a new path")
        return 2
    try:
        values = vars(args).copy()
        values.pop("format")
        values.pop("output")
        values["headless"] = not values.pop("headed")
        values["proxy_url"] = os.environ.get("CRAWLER_PROXY_URL") or None
        report = asyncio.run(scrape(Settings(**values)))
        output = json.dumps(asdict(report), ensure_ascii=False, indent=2) if args.format == "json" else "\n\n---\n\n".join(
            f"# {doc.title}\n\nSource: {doc.url}\n\n{doc.markdown}" for doc in report.documents
        )
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with output_file.open("x", encoding="utf-8") as destination:
                destination.write(output + "\n")
        else:
            print(output)
        for failure in report.failures:
            LOG.error("%s: %s (%s)", failure.category, failure.message, failure.url)
        return 2 if report.failures else 0
    except KeyboardInterrupt:
        return 130
    except FileLockTimeout:
        LOG.error("Another scraper is using this state directory; choose a different --state-dir")
        return 2
    except (ValueError, OSError) as error:
        LOG.error("Configuration/output error: %s", error)
        return 2
    except Exception as error:  # noqa: BLE001 — sanitize unknown library errors at the CLI boundary.
        # No raw third-party exception/traceback output: it may contain credentials or full HTML.
        LOG.error("Pipeline startup/runtime failed (%s). Check dependencies and browser installation.", type(error).__name__)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
