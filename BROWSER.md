# Project browser

The workspace uses `@amaster.ai/pi-browser-use` with `chrome-devtools-mcp` in headless persistent mode.

- Profile: `~/.pi/browser-profile`
- Configuration: `.pi/settings.json`
- Use this dedicated profile rather than personal Chrome.
- Call `browser_list_pages` before page-scoped browser tools and pass `pageId` explicitly.

## User-initiated login

When a platform requires login, the user may explicitly run:

```bash
python3 scripts/browser-login.py --headed-login URL
```

Close the headed profile owner before resuming headless browser use. The helper refuses to run without `--headed-login` and checks profile locks.

## When to use

Use the browser for interactive pages, authenticated sessions, Meta Ads Library, TikTok Creative Center/Commercial Content Library, and pages that simpler extractors cannot retrieve. Use `agent-web` or `scripts/scrape-web` for ordinary extraction and crawling.
