# Project browser

The workspace uses `@amaster.ai/pi-browser-use` with `chrome-devtools-mcp` in headless persistent mode.

- Profile: `~/.pi/browser-profile`
- Configuration: `.pi/settings.json`
- Use this dedicated profile rather than personal Chrome.
- Call `browser_list_pages` before page-scoped browser tools and pass `pageId` explicitly.

## Proxy routing

Never change macOS system proxy settings with `networksetup` or System Settings > Network. If a proxy is needed, configure it only in one browser profile and include its authentication. Why: system-wide proxy routing also affects the local model connection; an unauthenticated proxy cut off that connection with HTTP 407 (captain, 2026-10-08).

Before finishing browser work involving a proxy, confirm `scutil --proxy` still shows `HTTPEnable : 0` and `HTTPSEnable : 0`.

## User-initiated login

When a platform requires login, the user may explicitly run:

```bash
python3 scripts/browser-login.py --headed-login URL
```

Close the headed profile owner before resuming headless browser use. The helper refuses to run without `--headed-login` and checks profile locks.

## When to use

Use the browser for interactive pages, authenticated sessions, Meta Ads Library, TikTok Creative Center/Commercial Content Library, and pages that simpler extractors cannot retrieve. Use `agent-web` or `scripts/scrape-web` for ordinary extraction and crawling.
