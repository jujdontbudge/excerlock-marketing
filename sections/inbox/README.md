# Inbox: every automatic message to a creator

Automation may message a creator only through **the send gate** (`gate/`). Nothing else sends. Rule: `AGENTS.md`
("Automated messages: zero room for error"). Why: on 2026-10-14 reminders went to creators who had already signed,
the bot answered half a question with someone else's name in the examples, and it could not see the captain's own
messages. The old system (`raw/retired-inbox-2026-10-15/`) is retired.

## How a message gets sent
1. **Something proposes** an `Action` (a message type for one creator):
   - `flow.py`: the SideShift contract job (reminders at 6h and 12h, "send me your email" once she signs, the 36-hour withdrawal check);
   - `propose.py`: the inbox run. Claude Opus reads new messages with **read-only** tools and proposes an approved
     message type or escalates (`PROPOSE.md`); it cannot send, approve drafts or change rules;
   - `send.py`: a send the captain ordered. It records a **one-use approval** bound to her, the message type and the
     exact text; only such an approval lets a send skip quiet hours, the gap, draft mode and PAUSED. Words in an
     Action (`captain_order`) authorize nothing by themselves.
2. **The gate decides** (`gate/dispatch.py`, in this order):
   1. the type is switched on, or the captain ordered it;
   2. the send was never made before (idempotency key);
   3. the text renders from the approved template with only her name and declared fields;
   4. it takes a per-chat lock;
   5. it reads the whole chat **live** from SideShift and holds on any of:
      - a message with an unknown sender;
      - a recent attachment from her;
      - the wrong state ("pending" is never "unsigned": a handle request means she signed);
      - outside 9am–9pm US Eastern;
      - a recent message from us;
      - an unanswered question;
      - the same text already in the chat;
   6. it runs the Opus full-chat review, which must answer SEND;
   7. it reads the chat again and holds if anything changed;
   8. it sends through contacts-mcp.

   Every decision, with its reasons, is journaled forever.
3. **Holds and escalations wait for the captain.** If a creator is waiting on him and no approved type covers it, nothing is sent.

## Switches
| What | How |
|---|---|
| Stop all automatic sends | `touch sections/inbox/PAUSED` (captain-ordered sends still work). Remove the file to resume. |
| Let the inbox send replies by itself | `touch sections/inbox/INBOX_AUTO`. Without it (the default) every reply the inbox proposes is a draft for the captain, whatever its type's mode; scheduled flow messages (reminders, warm-up guide, email request) follow their own modes. |
| One message type on/off/draft | `mode:` in `messages/<id>.md` |
| New or changed wording | `approved: pending` forces draft until the captain approves the exact words |
| The jobs | `launchctl bootstrap gui/$(id -u) sections/inbox/launchd/com.excerlock.flow.plist` (and `.propose`); `launchctl bootout gui/$(id -u)/com.excerlock.flow` to stop. Copy the plist to `~/Library/LaunchAgents/` only if it should survive a restart. |

## Message types (`messages/`)
One file each; the front matter is documented in `gate/policy.py`. Today:
- `contract-invite`, `contract-reminder-1`, `contract-reminder-2`;
- `warmup-guide`, `ask-app-email`, `app-access` (free Premium: `~/.claude/skills/excerlock-access/SKILL.md`), `app-demo-setup`;
- `brief-on-interest`, `at-capacity`, `not-in-us`, `own-workflow`;
- `honest-review` (`mode: off` until approved demos are tracked).

Texts follow `core/writing-to-creators.md` (short, her own name in examples). Facts come from `core/creator-knowledge/`.

## The creator record
`record.py show "<name>"` prints one creator's whole story in order:
- every message, live from SideShift, including the captain's own;
- every gate decision;
- every state change (contract status, signed, handle checks, withdrawals);
- every captain decision.

Add `--html file.html` for a page. Record a decision with `record.py decide "<name>" "<decision>"`. Keep an invite from
being withdrawn with `record.py keep-invite "<name>" "<why>"`.

## Signing has two levels
- **Maybe signed**: a handle request for this campaign in SideShift's own records (`SIDESHIFT_READ_KEY`, a read-only
  key with 34 view permissions, created 2026-10-15), or a "📨 Requested handle … for this contract" notice in her chat,
  after this contract's invite. This only **stops** things (reminders, withdrawal). SideShift re-posts the invite link right after
  approving a handle; that repost is not a new invite (`gate/checks.py: invite_links`).
  Once seen by any part (flow, gate or withdrawal), it is journaled as `maybe-signed` for that contract and keeps stopping things even if the notice is later
  deleted or emptied. Records that can't be read also count as maybe signed, but only for that run; they are not journaled.
- **Signed**: the contract is `active` in SideShift (you approved her handles). Only this **starts** onboarding: the
  warm-up guide if she never got it, then "send me your email".

## Free Premium
When a signed creator sends her email, the inbox proposes `app-access`. The **gate** grants as its last step, after
every other check (pause, do-not-contact, a freshly re-read active contract, the email written in her live messages,
the review): `grant.py` runs `excerlock-access` (check, grant once, one owner per email, never retry blindly) and
records `premium-granted`; only then does the message go out. Right before the grant itself, after the slow entitlement
check, the gate re-checks everything again (contract, chat, do-not-contact, approval, switches), and the email's owner
is settled in one database transaction, so two creators can never end up with the same Premium account.

## Questions and attachments
A message counts as answered only when it is **marked** answered, and the mark covers that exact content (an edited
message needs a new mark): by the captain (`record.py answered "<name>" <message id>`), or by a gate reply whose full-chat
review confirmed it answered everything open. Writing something after it is not proof, not even from the captain.
Unmarked questions newer than the captain's last message block automatic sends outright; older ones go to the review. Her attachments block automation
until marked looked at (`record.py looked-at`). `record.py dnc "<name>" on` stops every automatic message to her.
A `do-not-contact` tag in contacts does the same, and once seen it stays on her account even if contacts later moves
the account to an untagged person; only `record.py dnc "<name>" off` releases it.

## Handles
When she signs, `gate/handles.py` checks the accounts she linked. New means:
- a TikTok created in the last 3 days;
- an Instagram with 0 posts and fewer than 50 followers;
- both platforms linked.

Usernames with "UGC" or "ExcerLock" fail (captain, 2026-10-15). The verdict (`pass`/`ask`/`fail`) is journaled. Only `pass` may ever be auto-approved, and only once a SideShift
key with `applications:write` exists. Until then the captain approves in SideShift.

## Data
- Journal: `~/Library/Application Support/ExcerLock/inbox-gate.db`. It's append-only: decisions and events can't be edited or deleted.
- `seed_journal.py` recorded the sends made before the gate existed.
- Logs: `~/Library/Logs/excerlock-inbox/`.

## Known limits (written down, not hidden)
- **The last split second.** SideShift has no conditional send. The sender reads the chat live once more right before
  sending, but a message she writes in the instant between that read and delivery can't be fenced by any client
  (pinned by an expected-failure test, `review4/test_gate_boundaries.py`).
- **Three sources, read one after another.** SideShift's chat, contract and handle-request records can't be read
  in one atomic step. The final checks re-read all of them and refuse to act if they took longer than 10 seconds
  together (`EVIDENCE_SPAN` in the gate, `SPAN` in withdrawals), so any remaining gap is seconds, not minutes.
- **Instagram account age.** Instagram doesn't show when an account was made; "new" there means 0 posts and under 50
  followers, so an Instagram is never treated as proven new on its own.
- **Email can't be read live yet.** Only SideShift chats are read live, so email replies always go to the captain.

## Tests
`.venv/bin/python -m unittest discover -s sections/inbox/gate/tests -t sections/inbox`. These are fakes only, no network.

Every real failure and review finding has a named test (`gate/tests/review2/` holds the second review's tests). Before any change to the gate goes live, run the tests,
break the change on purpose to see a test fail, and dry-run on real chats: `flow.py --dry-run`, `propose.py --dry-run`
and `send.py --dry-run`.
