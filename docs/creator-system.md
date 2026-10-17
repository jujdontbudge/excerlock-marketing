# The creator system, end to end

A map of every part that finds, signs, messages and tracks creators, and where each part's rules live. This page explains; the linked files decide. Diagram: `creator-system.excalidraw`.

## The parts

| Part | What it owns | Runs on | Home |
|---|---|---|---|
| **This repo** | Research, the creator brief, creator knowledge, message wording, the send gate, the creator database code | Air (live services) and Pro (agent work) | `AGENTS.md` |
| **Creator database** (`sections/creators`) | Every creator we look at: handles, stats snapshots, vetting score, stage, deals, contracts, posts, payouts | Air, `~/excerlock-creators/`, SQLite `data/creators.db`, backed up daily | `sections/creators/README.md` |
| **SideShift** | The marketplace where creators apply, chat with us, sign the contract and link their accounts | SideShift's servers; we use its API | `integrations/sideshift/README.md` |
| **contacts-mcp** | One person ID per human across every channel (SideShift, iMessage, email, TikTok, Instagram), every message stored, the only thing that sends | Air, separate repo `JohanSardar/contacts-mcp`, daemon on `127.0.0.1:8787` | `~/contacts-mcp/README.md`, `integrations/contacts-mcp/README.md` |
| **Send gate** (`sections/inbox`) | Every automatic message to a creator: which types may go, when, and the checks before each one | Air, launchd jobs every 15 minutes | `sections/inbox/README.md` |
| **Free Premium** | Giving a signed creator ExcerLock Premium by email | Air, `excerlock-access` skill | `~/.claude/skills/excerlock-access/SKILL.md` |
| **Dashboard** | One page for the captain: approval inbox, boards, what the gate is holding | Air, tailnet only | `sections/creators/README.md` |

## A creator's path

1. **Found.** From the hunts (`raw/creators/`), SideShift applicants (`sideshift-creators sync`) or a link the captain adds (`creators add`). Each becomes one record in the creator database, scored by Jake's 20-second test.
2. **Contacted.** Outreach drafts wait for the captain unless their kind is switched on. On SideShift, the conversation happens in its chat.
3. **Invited.** The captain sends the SideShift contract (`contract-invite`).
4. **Reminded.** If she hasn't accepted, `flow.py` proposes `contract-reminder-1` at 6 hours and the last-call `contract-reminder-2` at 12 ("stays open for 12 more hours"). At 24 hours, and at least 12 hours after the last-call, it records that a withdrawal is due; withdrawing is a separate step and never messages her.
5. **Accepted ("maybe signed").** She links her new TikTok and Instagram, and a "📨 Requested handle" notice appears. SideShift still says `pending`, which does **not** mean unsigned. From here no reminder or withdrawal can fire. `gate/handles.py` checks the accounts are new.
6. **Signed.** The captain approves her handles and the contract turns `active`. The flow sends the `warmup-guide` (if she never got one), then `ask-app-email`.
7. **Premium.** She sends her email. The inbox proposes `app-access`; the gate grants Premium as its very last step, one account per creator, then the message goes.
8. **Posting and paid.** Deliverables, post tracking, 1/3/7-day performance and payouts live in the creator database (`sections/creators/README.md`, steps 9–11).

## How a message gets sent

Nothing messages a creator except the gate. Three things can ask it to: the contract flow (`flow.py`), the inbox reader (`propose.py`, which reads new messages and can only propose) and the captain (`send.py`, a one-use approval for exact words). For every request the gate checks the type is approved and switched on, renders the approved words, reads her whole chat live from SideShift, holds on anything unclear (her unanswered question, an attachment, a recent message from us, outside 9am–9pm Eastern, wrong contract state), asks a full-chat review to say SEND, reads again, and only then sends through contacts-mcp. Every decision and reason is journaled forever (`~/Library/Application Support/ExcerLock/inbox-gate.db`). The full order of checks is in `sections/inbox/README.md`.

What runs by itself today (captain's choice "c", 2026-10-15): contract reminders, the warm-up guide and the email request. Inbox replies and Premium messages are drafts for the captain. Withdrawals are never automatic.

## Switches the captain uses

| To | Do |
|---|---|
| Stop every automatic message | `touch sections/inbox/PAUSED` |
| Turn one message type on, off or to draft | `mode:` in `sections/inbox/messages/<id>.md` |
| Stop messages to one creator | `sections/inbox/record.py dnc "<name>" on` |
| See one creator's whole story | `sections/inbox/record.py show "<name>"` |
| Send something now | `sections/inbox/send.py --creator "<name>" --type <id>` or `--text "<exact words>"` |

## Where answers and wording come from

- Facts and approved answers creators get: `core/creator-knowledge/`.
- How anything a creator reads is written: `core/writing-to-creators.md`.
- The brief creators film from: `sections/real-ugc/README.md`.

## Known limits

Written down with their reasons in `sections/inbox/README.md` ("Known limits") and `sections/creators/README.md` ("Not built yet"): the last split second before a send can't be fenced, SideShift's records can't be read in one atomic step, Instagram account age isn't visible, email replies aren't read live yet, payouts are manual until PayPal/Wise accounts exist.
