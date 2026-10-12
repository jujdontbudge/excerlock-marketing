# Creators (UGC and influencer pipeline)

Finds, vets, contacts, signs, schedules, tracks and pays real creators, and feeds what worked back into the next round. Diagram: `docs/creator-system.excalidraw`. Why it is software in a research repo: `docs/adr/0005-creator-system-is-code.md`.

## Where it runs
The MacBook Air (`johansardar@100.78.200.121`, always on) hosts it under `~/excerlock-creators/` as launchd user agents:

| Service | What | Address |
|---|---|---|
| `com.excerlock.creators.dashboard` | approval inbox and boards | https://johansardars-macbook-air.tail2ea909.ts.net:8443 (tailnet only, Tailscale Serve) |
| `com.excerlock.creators.portal` | creator pages (sign, payout details, hand in) and the Resend webhook | https://johansardars-macbook-air.tail2ea909.ts.net (public, Tailscale Funnel) |
| `com.excerlock.creators.jobs` | `creators jobs` every 3 hours | |
| `com.excerlock.creators.backup` | daily SQLite backup, keeps 30 | `data/backups/` |

```
sections/creators/deploy               # push code + keys from .env, (re)install services, Funnel/Serve
sections/creators/remote jobs          # run any creators command on the Air
sections/creators/remote tunnel        # dashboard on http://127.0.0.1:8765 over ssh instead of the tailnet
```

Deploy also syncs the repository's `AGENTS.md` and Claude's `CLAUDE.md` import to the Air's application root, so agents there read the same operating instructions.

## Use it
```
sections/creators/creators add https://www.tiktok.com/@name ig:other tt:third   # or --file links.txt
sections/creators/creators jobs        # refresh, score, follow-ups, reminders, find + measure posts, payouts, send approved
sections/creators/creators serve       # dashboard on http://127.0.0.1:8765
sections/creators/creators portal      # creator pages on http://127.0.0.1:8766
sections/creators/creators ig-login    # log the research Instagram account into data/ig-browser (--headed to watch, --cookies file to import)
sections/creators/creators backup
```

## The flow
1. **Intake** (`creatorops/intake.py`): any TikTok/Instagram profile or post link, `tt:`/`ig:` handle or email. Same handle twice is the same person; other handles and emails found in a bio are attached automatically.
2. **Snapshot** (`creatorops/snapshot.py`): dated stats per handle: followers, median views of the last 20 posts, posts in 30 days, comments from the 3 most-commented posts. Stale after 7 days. TikTok is read from public pages and yt-dlp; Instagram from page views in a logged-in Chrome (`platforms/instagram_browser.py`), because Instagram's JSON API answers 429 to scripts.
3. **Vetting** (`creatorops/vetting.py`): Jake's 20-second test as a 0-100 score with reasons, the track (influencer from 15k median views, else UGC), and an AI note on content type, audience, parasocial pull and fit.
4. **Pipeline** (`creatorops/pipeline.py`): the only place a stage changes; illegal moves raise. Do-not-contact blocks every draft.
5. **Outreach** (`creatorops/outreach.py`, templates in `templates/`): first message, follow-ups (after 4 days, max 2, then no_reply) and post-day reminders. Email goes through Resend; TikTok/Instagram DMs are only drafted for a human to paste.
6. **Replies** (`creatorops/inbound.py`): mail to `CREATORS_REPLY_TO` is forwarded to Resend Receiving, whose signed `email.received` webhook hits the portal's `/hooks/resend`. The reply is stored, the person moves to replied, and "no" or "unsubscribe" sets do-not-contact.
7. **Deals** (`creatorops/deals.py`): terms in; `brief.md`, `contract.md` and a private portal link out. The offer email carries the link.
8. **Contract** (`creatorops/portal.py`): the creator reads the contract, ticks consent to sign electronically and agreement, and types their name. The signature stores the exact text and its SHA-256, IP, browser and time, writes `contract-signed.md` and emails both sides a copy (E-SIGN/UETA click-to-sign). Signing schedules posts on randomized days and owes the upfront payment.
9. **Deliverables** (`creatorops/deliverables.py`): drafts and post links handed in on the portal, draft review, finding the live post by promo code or match terms, lateness.
10. **Performance** (`creatorops/performance.py`): views, likes, comments and "what app is this?" comments at 1, 3 and 7 days; renew / fix / cut verdict; balance owed when every video is live.
11. **Payouts** (`creatorops/payouts.py`): the creator enters a PayPal email or Wise details on the portal; approving a payment in the dashboard sends it through `CREATORS_PAYOUTS` and `jobs` checks its status. Retries are idempotent (PayPal `sender_batch_id`, Wise `customerTransactionId`).

## What waits for the captain
Picking who to contact, every message (unless its kind is listed in `CREATORS_AUTO_SEND`, e.g. `reminder,followup`), deal terms, video drafts and payouts. Why: `AGENTS.md` asks before anything that spends money or speaks for the brand.

## Settings (`.env`; `deploy` copies the `RESEND_*`, `CREATORS_*`, `PAYPAL_*`, `WISE_*`, `IG_SCRAPER_*` lines)
- Email: `RESEND_API_KEY` (send), `RESEND_FULL_API_KEY` (read received mail), `RESEND_WEBHOOK_SECRET`, `CREATORS_FROM`, `CREATORS_REPLY_TO`.
- Instagram: `IG_SCRAPER_USER`, `IG_SCRAPER_PASSWORD` (the research account, used by `ig-login`).
- Payouts: `CREATORS_PAYOUTS` (`manual` default, `paypal`, `wise`); `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, `PAYPAL_ENV` (`sandbox`/`live`); `WISE_TOKEN`, `WISE_ENV`.
- Other: `CREATORS_AUTO_SEND`, `CREATORS_ROUTING_MEDIAN` (15000), `CREATORS_PUBLIC_URL` (set by `deploy`), `CREATORS_JUDGE_CMD` (default `claude -p --model haiku`; on the Air `deploy` sets `codex exec`, because Codex is logged in there and Claude is not).

## Seams
Only three, because only these vary: platform (`creatorops/platforms/`: TikTok, Instagram), message channel (`creatorops/channels.py`: email, DM) and payout provider (`creatorops/payouts.py`: manual, PayPal, Wise). Tests use the fakes in `tests/fakes.py` and a fake HTTP layer as the second adapter.

## Tests
- Offline, whole lifecycle including portal signing, webhook signatures and payout idempotency: `.venv/bin/python sections/creators/tests/test_offline.py` (part of `scripts/test`).
- Live, real accounts and real sends: `LIVE=1 .venv/bin/python sections/creators/tests/test_live.py` (`CREATORS_LIVE_NO_JUDGE=1` skips the AI note).

## Data
`data/` is gitignored: the store (`creators.db`), backups, generated briefs and signed contracts, the Instagram browser profile. It holds creators' emails, names and payout details; never commit it.

## Not built yet
Promo-code installs (needs per-creator codes or links in the app or RevenueCat), automatic tax forms (collect a W-9/W-8BEN by hand for US payees), a phone share-sheet shortcut, and live PayPal/Wise payouts (needs the captain's PayPal Business or Wise account and keys; until then payments are marked paid by hand).
