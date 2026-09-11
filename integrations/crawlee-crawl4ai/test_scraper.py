"""Local deterministic JS/server fixtures; no third-party browsing or paid services."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import pairwise
from pathlib import Path

import pytest
from filelock import FileLock

from scraper import Settings, chunk_markdown

SCRIPT = Path(__file__).with_name("scraper.py")


@contextmanager
def fixture_site() -> Iterator[tuple[str, Counter[str]]]:
    counts: Counter[str] = Counter()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args: object) -> None:
            pass

        def do_GET(self) -> None:
            counts[self.path] += 1
            status = 200
            if self.path == "/robots.txt":
                content = "User-agent: *\nDisallow: /forbidden\n"
                mime = "text/plain"
            elif self.path in {"/403", "/429"}:
                status = int(self.path[1:])
                content, mime = "Access denied", "text/plain"
            elif self.path == "/challenge":
                content, mime = "<html><title>Just a moment...</title><body>Verify you are human</body></html>", "text/html"
            elif self.path == "/api":
                content, mime = json.dumps({"message": "Rendered JavaScript research contains verified product information and useful commercial context."}), "application/json"
            elif self.path == "/flaky" and counts[self.path] < 3:
                status, content, mime = 500, "Temporary fixture error", "text/plain"
            elif self.path == "/":
                mime = "text/html"
                content = f'''<!doctype html><html><head><title>Fixture research</title></head>
<body><header>HEADER_JUNK</header><nav>NAV_JUNK <a href="/junk">Sign in now</a></nav>
<main id="main">Loading</main><footer>FOOTER_JUNK</footer>
<script>
const returning = localStorage.getItem('visited') === 'yes';
const returningCookie = document.cookie.includes('fixture_cookie=present');
localStorage.setItem('visited', 'yes');
document.cookie = 'fixture_cookie=present; path=/';
setTimeout(async () => {{
 const data = await (await fetch('/api')).json();
 document.querySelector('#main').innerHTML = `<article id="ready"><h1>Research fixture article</h1>
 <p>${{data.message}}</p><p>${{returning ? 'RETURNING_SESSION' : 'FIRST_SESSION'}} browser storage preserves this complete research session.</p>
 <p>COOKIE_STATE ${{document.cookie}} ${{returningCookie ? 'RETURNING_COOKIE' : 'FIRST_COOKIE'}} is present in this browser owned research profile.</p>
 <p>The following plan comparison describes available features for a fictional product research fixture only.</p>
 <table><thead><tr><th>Plan</th><th>Price</th><th>Feature</th></tr></thead>
 <tbody><tr><td>Basic</td><td>10</td><td>Core reports</td></tr><tr><td>Pro</td><td>20</td><td>Detailed reports</td></tr></tbody></table>
 <p>Read <a href="/detail">the detailed research information</a> for another useful article about this fixture.</p>
 <a href="http://localhost:{self.server.server_port}/outside">Different origin</a></article>`;
}}, 100);
</script></body></html>'''
            else:
                mime = "text/html"
                content = '<html><head><title>Detail fixture</title></head><body><article id="ready"><h1>Detail fixture article</h1><p>Detailed research provides meaningful evidence for testing this rendered document processing pipeline without accessing any remote service.</p></article></body></html>'
            data = content.encode()
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", counts
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def run_cli(url: str, state: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env.pop("CRAWLER_PROXY_URL", None)
    env.pop("PLAYWRIGHT_BROWSERS_PATH", None)  # Use the explicitly installed Playwright browser.
    return subprocess.run(
        [sys.executable, str(SCRIPT), url, "--state-dir", str(state), "--format", "json",
         "--settle-seconds", "0", "--scroll-steps", "0", *extra],
        env=env, capture_output=True, text=True, timeout=75, check=False,
    )


def test_chunk_offsets_coverage_bounds_and_stable_ids() -> None:
    text = "# Heading\n\n" + ("Meaningful text with Unicode café and useful context.\n\n" * 70)
    chunks = chunk_markdown(text, "https://example.com/", 300, 40)
    assert len(chunks) > 1
    assert chunks == chunk_markdown(text, "https://example.com/", 300, 40)
    assert chunks[0].start_char == 0 and chunks[-1].end_char == len(text)
    for chunk in chunks:
        assert chunk.text == text[chunk.start_char:chunk.end_char]
        assert len(chunk.text) <= 300
    for previous, following in pairwise(chunks):
        assert previous.start_char < following.start_char <= previous.end_char


@pytest.mark.parametrize("kwargs", [
    {"url": "file:///etc/passwd"}, {"url": "https://user:secret@example.com"},
    {"url": "https://example.com", "max_pages": 0},
    {"url": "https://example.com", "chunk_chars": 200, "overlap_chars": 100},
    {"url": "https://example.com", "proxy_url": "invalid-proxy"},
    {"url": "https://example.com", "total_timeout": float("nan")},
    {"url": "https://example.com", "link_selector": " "},
])
def test_invalid_config(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        Settings(**kwargs)


def test_js_raw_handoff_and_persistent_local_storage(tmp_path: Path) -> None:
    with fixture_site() as (url, counts):
        first = run_cli(url, tmp_path / "state", "--wait-selector", "#ready")
        assert first.returncode == 0, first.stderr
        result = json.loads(first.stdout)
        doc = result["documents"][0]
        assert "Rendered JavaScript" in doc["markdown"]
        assert "FIRST_SESSION" in doc["markdown"]
        assert "fixture_cookie=present" in doc["markdown"]
        assert "HEADER_JUNK" not in doc["markdown"]
        assert "NAV_JUNK" not in doc["markdown"]
        assert "FOOTER_JUNK" not in doc["markdown"]
        assert "<script" not in doc["markdown"]
        assert "Pro" in doc["markdown"] and "Detailed reports" in doc["markdown"]
        assert f"{url}/detail" in doc["markdown"]
        assert counts["/"] == 1 and counts["/api"] == 1  # Crawl4AI did not refetch or execute JS.
        second = run_cli(url, tmp_path / "state", "--wait-selector", "#ready")
        assert second.returncode == 0, second.stderr
        second_markdown = json.loads(second.stdout)["documents"][0]["markdown"]
        assert "RETURNING_SESSION" in second_markdown
        assert "RETURNING_COOKIE" in second_markdown
        assert list((tmp_path / "state" / "crawlee").rglob("CRAWLEE_SESSION_POOL_STATE"))
        assert counts["/"] == 2


@pytest.mark.parametrize("path", ["/403", "/429", "/challenge"])
def test_blocked_requests_are_not_retried(tmp_path: Path, path: str) -> None:
    with fixture_site() as (url, counts):
        result = run_cli(url + path, tmp_path / "state")
        assert result.returncode == 2, result.stderr
        report = json.loads(result.stdout)
        assert not report["documents"]
        assert report["failures"][0]["category"] == "blocked"
        assert counts[path] == 1


def test_transient_server_errors_retry(tmp_path: Path) -> None:
    with fixture_site() as (url, counts):
        result = run_cli(url + "/flaky", tmp_path / "state")
        assert result.returncode == 0, result.stderr
        assert counts["/flaky"] == 3
        assert len(json.loads(result.stdout)["documents"]) == 1


def test_robots_exclusion(tmp_path: Path) -> None:
    with fixture_site() as (url, counts):
        result = run_cli(url + "/forbidden", tmp_path / "state")
        assert result.returncode == 2, result.stderr
        assert counts["/forbidden"] == 0
        assert not json.loads(result.stdout)["documents"]


def test_bounded_same_origin_traversal(tmp_path: Path) -> None:
    with fixture_site() as (url, counts):
        result = run_cli(url, tmp_path / "state", "--wait-selector", "#ready", "--max-pages", "2")
        assert result.returncode == 0, result.stderr
        assert len(json.loads(result.stdout)["documents"]) == 2
        assert counts["/outside"] == 0
        assert counts["/detail"] == 1


def test_output_overwrite_is_rejected_before_network(tmp_path: Path) -> None:
    output = tmp_path / "existing.json"
    output.write_text("keep this file", encoding="utf-8")
    result = run_cli("https://example.invalid", tmp_path / "state", "--output", str(output))
    assert result.returncode == 2
    assert output.read_text(encoding="utf-8") == "keep this file"
    assert "Output already exists" in result.stderr


def test_state_lock_prevents_parallel_browser_profile_use(tmp_path: Path) -> None:
    state = tmp_path / "state"
    state.mkdir()
    with FileLock(str(state / "pipeline.lock")):
        result = run_cli("https://example.invalid", state)
    assert result.returncode == 2
    assert "Another scraper is using this state directory" in result.stderr


def test_deadline_is_structured_failure(tmp_path: Path) -> None:
    with fixture_site() as (url, _counts):
        result = run_cli(url, tmp_path / "state", "--total-timeout", "0.05")
        assert result.returncode == 2, result.stderr
        assert json.loads(result.stdout)["failures"][0]["category"] == "timeout"
