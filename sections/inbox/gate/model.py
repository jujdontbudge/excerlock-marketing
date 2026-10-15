"""Plain data the send gate passes around. No I/O here."""
from dataclasses import dataclass, field
from typing import Optional

IN, OUT, UNKNOWN = 'in', 'out', 'unknown'


@dataclass(frozen=True)
class Msg:
    id: str
    at: str                 # ISO-8601 UTC, as the source gave it
    direction: str          # IN (the creator), OUT (us: captain or company bot), UNKNOWN (never guessed)
    author: str             # 'creator' | 'captain' | 'company' | 'unknown'
    text: str
    kind: str = 'text'      # 'text' | 'handle_request' | 'handle_approved' | 'invite_link' | 'system'
    deleted: bool = False
    attachments: int = 0
    attachments_sig: str = ''   # fingerprint of WHICH attachments (ids/urls), so a swapped image needs a new look (R04)
    edited_at: str = ''     # '' not edited; ISO time of the edit; 'unknown' = edited, time unusable (review BQ01)
    vanished: bool = False  # from the journal: seen on an earlier read, no longer in the chat in this form (review AY01)


@dataclass(frozen=True)
class Conversation:
    source: str             # 'sideshift'
    external_id: str        # the source's own chat id
    creator_ids: tuple      # the creator's source user ids in this chat
    messages: tuple         # Msg, oldest first, complete
    fingerprint: str        # changes whenever any message is added, edited or deleted
    read_at: str            # when we read it live
    complete: bool = True   # False for what a failed read got before failing: veto evidence only (review AE02, AG01)
    creator_name: str = ''  # her name on the SideShift chat as read now ('' when unknown) (review BP01)


@dataclass
class Action:
    """One message we might send. Producers (reminders, the inbox agent, the captain via Claude) only create these."""
    message_type: str
    channel: str
    conversation_id: str            # contacts-mcp conversation id (the send route)
    source_chat_id: str             # the source's chat id, read live before sending
    person_id: Optional[str]
    creator_key: str                # stable id for the journal, e.g. 'sideshift:<userId>'
    fields: dict = field(default_factory=dict)
    trigger: str = ''               # what caused it, e.g. 'contract:<id> age 6h'
    occurrence: str = ''            # makes the idempotency key; e.g. the contract id for per-contract types
    captain_order: Optional[str] = None   # the captain's own words when he ordered this exact send (journal only)
    approval_id: Optional[str] = None     # one-use approval made by the captain's command; the only thing that authorizes
    contract: Optional[dict] = None       # the SideShift contract this is about, when it is about one


@dataclass
class Decision:
    outcome: str                    # 'sent' | 'held' | 'draft' | 'error' (definitely not sent) | 'uncertain' | 'dispatching'
    reasons: list
    text: str = ''
    idempotency_key: str = ''
    fingerprint: str = ''
    outbox_id: Optional[str] = None
