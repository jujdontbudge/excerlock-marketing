# Inbox automation

Answers new messages to ExcerLock's business accounts (email, Instagram, TikTok, SideShift) within 15 minutes. If one of the captain's rules covers a message, it replies automatically. Everything else goes to the captain.

## How it runs
- **Schedule:** a T3 Code scheduled task, every 15 minutes, on the MacBook Air. The task's prompt never changes: it only says to read `RUN.md` and follow it. **To change behaviour, edit the files here, never the schedule.**
- **Agent:** Codex (gpt-6.1-sol), with the `contacts` MCP (contacts-mcp on the Air).
- **Never twice:** contacts-mcp keeps a state for every inbound message and refuses to reuse a send key. Why: the agent can crash or overlap with another run, and the captain must never get a double reply sent in his name (2026-10-12).
  - States: `new`, `claimed`, `auto_replied`, `escalated`, `ignored`, `done`.
  - Tools: `list_inbox`, `claim_inbox`, `mark_inbox`, and `send_message` with an `idempotency_key`.
- **Not personal texts:** iMessage is the captain's personal phone and is never read or answered here.
- **Results:** every run reports in its T3 thread. "Needs you" items are the escalations.

## Files
| Path | What |
|---|---|
| `RUN.md` | The steps every run follows |
| `rules/*.md` | One file per rule. The file name is the rule id |
| `PAUSED` | If this file exists, runs do nothing: the off switch for all automatic sending |

## Add, change or remove a rule
- **Add:** copy `rules/_example.md` to `rules/<id>.md`.
  - Fill in **When**, **Not when** and **Reply** in plain words. **Reply** holds the exact text the captain approved.
  - Start new rules at `mode: draft` unless the captain approved sending automatically. Draft mode puts the reply in the approval inbox instead of sending it.
- **Change:** edit the file. The next run uses it.
- **Turn off:** set `mode: off`. Don't delete the file: past sends refer to the rule id.
- **Stop everything:** create `PAUSED`. Delete it to resume.

### Rule file format
```
---
mode: auto            # auto = send automatically · draft = approval inbox · off = ignored
channels: [email, instagram, tiktok]
once_per_person: true # true = this person gets this reply at most once, ever
approved: 2026-10-12  # when the captain approved the wording
---
## When
Who this rule is for, in plain words.
## Not when
Cases that look similar but must go to the captain.
## Reply
Subject: (email only)
The exact message. {first_name} is the person's first name.
```
