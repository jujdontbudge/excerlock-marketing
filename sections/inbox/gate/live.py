"""Live, complete read of one SideShift chat, straight from SideShift (never the contacts-mcp copy).

Direction is decided only from identity fields we have proven on real messages (2026-10-14):
- the creator's messages carry her SideShift user id in `senderUserId`, and that id is a chat member;
- the captain's own messages carry the company id (`senderUserId` == company id, shown as "Johan Sardar");
- our API sends and SideShift's own notices carry no user id and `sender` == the company name ("Excerlock").
Anything else is UNKNOWN, and the gate refuses to send while a chat contains an UNKNOWN message.

Everything that can go wrong while reading or normalizing (transport, odd fields, stored fallbacks, empty history)
becomes LiveReadError, so the gate holds instead of crashing (review G08, G25).
"""
import hashlib
from dataclasses import replace
import json
import re
import uuid
from datetime import datetime, timezone

from .model import IN, OUT, UNKNOWN, Conversation, Msg

HANDLE_REQUEST = re.compile(r'^📨 Requested (\d+ )?handles?\b.*for this contract', re.S)
HANDLE_APPROVED = re.compile(r'^✅ Your handle @\S+ .* was approved for ', re.S)
# The exact shape of SideShift's own handle-request notice (checked against every real one, 2026-10-15). Only this exact
# text is exempt from "she may be waiting for an answer"; anything else, even if it starts like a notice, is hers (AN02).
REQUEST_NOTICE_EXACT = re.compile(r'📨 Requested (?:\d+ handles: |handle )@[^\s?]+ \(\w+\)(?:, @[^\s?]+ \(\w+\))* '
                                  r'for this contract\.(?:\n\n🎯 Campaign: [^\n?]+)?')
INVITE_LINK = re.compile(r'^https://app\.sideshift\.app/campaign-invite/([A-Za-z0-9_-]+)(\?\S*)?$')


class LiveReadError(RuntimeError):
    """No complete live read. `partial` is what WAS read and validated before the failure (a Conversation), or None.
    It may only ever add a veto (signing evidence), never permit anything (review AE02)."""
    def __init__(self, message, partial=None):
        super().__init__(message)
        self.partial = partial


def application_owner(a, campaign):
    """Who a handle-request row belongs to, or None when it is not for this campaign. A row we can't read (not a
    record, no campaign, no creator) raises: it may be hers, so coverage becomes unknown, never "none" (review AK01)."""
    if not isinstance(a, dict):
        raise ValueError('unreadable handle-request record')
    program = a.get('programId')
    if not isinstance(program, str) or not program:
        raise ValueError('handle-request record without a readable campaign')
    if program != campaign:
        return None
    join = a.get('isJoinRequest')
    if join is not None and not isinstance(join, bool):   # "false" is not False: only a real boolean excludes (AL01)
        raise ValueError('handle-request record with an unreadable join flag')
    if join:
        return None
    creator = a.get('creator')
    owner = creator.get('id') if isinstance(creator, dict) else None
    if not isinstance(owner, str) or not owner:   # only a readable id proves whose it is (AL01)
        raise ValueError('handle request for this campaign with no readable creator')
    return owner


def collect_contracts(client, campaign, on_row=None):
    """The campaign's contracts. Each row goes to on_row the moment it is read, before the next page, so an active
    contract (signing evidence) is never held only in memory (review AJ02)."""
    out = []
    for c in client.pages('/contracts', programId=campaign):
        if isinstance(c, dict) and on_row is not None:
            on_row(c)
        out.append(c)
    return out


def collect_applications(client, campaign, uid, on_row=None):
    """Her handle requests for this campaign. If a later page fails, the rows already read ride on the exception as
    `exc.partial`: they still prove requests, while coverage stays unknown (review AD01, AE01)."""
    out = []
    try:
        for a in client.pages('/applications'):
            owner = application_owner(a, campaign)   # unreadable rows make coverage unknown (AK01)
            if owner is None:
                continue
            if on_row is not None:   # EVERY creator's row, under its own creator, before the next page (AH02, AI02)
                on_row(owner, a)
            if owner == uid:
                out.append(a)
    except Exception as exc:
        exc.partial = out
        raise
    return out


def classify(text):
    t = (text or '').strip()
    if HANDLE_REQUEST.match(t):
        return 'handle_request'
    if HANDLE_APPROVED.match(t):
        return 'handle_approved'
    if INVITE_LINK.match(t):
        return 'invite_link'
    return 'text'


def invite_contract_id(text):
    m = INVITE_LINK.match((text or '').strip())
    return m.group(1) if m else None


def instant(value):
    """Validated aware UTC datetime from an ISO string; anything else raises ValueError."""
    if not isinstance(value, str) or not value:
        raise ValueError('timestamp missing')
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('naive timestamp')
    return dt.astimezone(timezone.utc)


def attachment_count(raw):
    count = raw.get('attachmentCount')
    listed = raw.get('attachments')
    n = 0
    if count is not None:
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError('bad attachmentCount')
        n = count
    if listed is not None:
        if not isinstance(listed, list):
            raise ValueError('bad attachments')
        n = max(n, len(listed))
    return n


FIELD_TYPES = {   # every field the checks rely on must have its real type; anything else is an unreadable message
    'id': str, 'createdAt': str, 'timestamp': str, 'updatedAt': str, 'isDeleted': bool, 'isEdited': bool,
    'senderUserId': str, 'senderExternalUserId': str, 'sender': str, 'senderName': str, 'source': str,
}   # checked against 292 live messages on 2026-10-15; None or absent is allowed (review AM01: "false" is not False)


def to_msg(raw, company_id, company_name, members):
    if not isinstance(raw, dict):
        raise ValueError('unreadable message record')
    for field, kind in FIELD_TYPES.items():
        if raw.get(field) is not None and not isinstance(raw[field], kind):
            raise ValueError(f'message field {field} has an unreadable value')
    if raw.get('source') not in (None, 'native'):
        raise ValueError(f"non-live message source {raw.get('source')!r}")
    sender_id = raw.get('senderUserId')
    sender = raw.get('sender') or raw.get('senderName')
    if sender_id and sender_id == company_id:
        direction, author = OUT, 'captain'
    elif sender_id and sender_id in members:
        direction, author = IN, 'creator'
    elif not sender_id and not raw.get('senderExternalUserId') and sender == company_name:
        direction, author = OUT, 'company'
    else:
        direction, author = UNKNOWN, 'unknown'
    text = raw.get('content')
    if text is None:
        text = ''
    if not isinstance(text, str):
        raise ValueError('content is not text')
    at = raw.get('createdAt') or raw.get('timestamp')
    if not raw.get('id'):
        raise ValueError('message without id')
    listed = raw.get('attachments') if isinstance(raw.get('attachments'), list) else []
    if listed and fully_identified(raw):   # stable ids for EVERY attachment: a refreshed URL is the same image (S16)
        ids = [a['id'] for a in listed]
        basis = json.dumps(sorted(map(str, ids)))
    elif listed or attachment_count(raw):   # no ids: any revision of the message counts as a new look needed (S15)
        revision = usable_revision(raw)
        if revision is None:   # no ids AND no usable revision time: the file details themselves are its identity, so
            # any change (another file, another name or link) needs a new look; unchanged details are the same file
            # (AN01, AO01, BJ01)
            if isinstance(listed, list) and listed and all(isinstance(a, dict) and a for a in listed):
                basis = 'payload:' + json.dumps([listed, raw.get('attachmentCount')], sort_keys=True, default=str)
            else:   # only a count, nothing to tell one file from another: never settleable, automation holds (AN01)
                basis = 'unidentifiable:' + uuid.uuid4().hex
        else:
            basis = json.dumps([listed, revision, raw.get('attachmentCount'), raw.get('isEdited')],
                               sort_keys=True, default=str)
    else:
        basis = ''
    sig = hashlib.sha256(basis.encode()).hexdigest()[:12] if basis else ''
    if basis.startswith('payload:'):
        sig = PAYLOAD + sig   # identity from the file details themselves (BJ01)
    elif basis.startswith('unidentifiable:'):
        sig = UNIDENTIFIABLE + sig   # per read: no look can cover it; history keeps one revision (AZ01)
    return Msg(id=str(raw['id']), at=instant(at).isoformat(), direction=direction, author=author, text=text,
               kind=classify(text), deleted=bool(raw.get('isDeleted')), attachments=attachment_count(raw), attachments_sig=sig,
               edited_at=((usable_revision(raw) or 'unknown') if raw.get('isEdited') is True else ''))   # (BQ01)


SAFETY_FIELDS = ('id', 'createdAt', 'timestamp', 'updatedAt', 'isDeleted', 'isEdited', 'content', 'senderUserId',
                 'senderExternalUserId', 'sender', 'senderName', 'attachmentCount', 'attachments', 'source')


UNIDENTIFIABLE = 'u-'   # per-read random: a file with nothing to identify it, never settleable
PAYLOAD = 'x-'          # file identity taken from the exact file details when there is nothing better (BJ01)


def revision_key(m):
    """What makes two reads the same revision of a message: its id, words and attachments (review AZ01)."""
    sig = UNIDENTIFIABLE if (m.attachments_sig or '').startswith(UNIDENTIFIABLE) else (m.attachments_sig or '')
    meta = content_sha(f'{m.at}|{m.direction}|{m.author}|{m.kind}|{m.edited_at}')   # who, when, kind, edit (BB01, BQ01)
    return f'{m.id}#{content_sha(m.text)}#{m.attachments}#{sig}#{int(bool(m.deleted))}#{meta}'   # deletion too (BA01)


def content_sha(text):
    """Short fingerprint of a message's content, so a mark ('answered', 'looked at') covers only what was seen."""
    return hashlib.sha256((text or '').encode()).hexdigest()[:12]


TRANSPORT = ('url', 'downloadUrl', 'thumbnailUrl', 'signedUrl', 'previewUrl')


def fully_identified(raw):
    """Every attachment is a dict with its own id, and the count agrees (review S15)."""
    listed = raw.get('attachments')
    if not isinstance(listed, list) or not listed:
        return False
    count = raw.get('attachmentCount')
    return all(isinstance(a, dict) and valid_attachment_id(a.get('id')) for a in listed) and (count is None or count == len(listed))


def valid_attachment_id(value):
    """Only non-blank text is an attachment id; True, numbers or blanks are not proof of the same file (AO01)."""
    return isinstance(value, str) and bool(value.strip())


def usable_revision(raw):
    """updatedAt as a real timezone-aware time, or None: a blank or garbled one can't tell edits apart (AO01)."""
    try:
        return instant(raw.get('updatedAt')).isoformat() if raw.get('updatedAt') else None
    except Exception:
        return None


def _stable(r):
    out = {k: r.get(k) for k in SAFETY_FIELDS}
    if isinstance(out.get('attachments'), list) and fully_identified(r):   # links are transport only when ids cover all (U02)
        out['attachments'] = [{k: v for k, v in a.items() if k not in TRANSPORT} if isinstance(a, dict) else a
                               for a in out['attachments']]
    return out


def fingerprint(raws, members=()):
    """Changes whenever anything the gate's checks look at changes: content, time, identity, attachments, members,
    and ORDER (same-time messages keep SideShift's order, which decides the invite round; review T03)."""
    basis = {'members': sorted(members), 'messages': [
        json.dumps(_stable(r), sort_keys=True, ensure_ascii=False, default=str) for r in raws]}
    return hashlib.sha256(json.dumps(basis, sort_keys=True).encode()).hexdigest()[:20]


# what identifies a signing notice; every other field (media, edit flags, revision) is irrelevant to it (AS01)
NOTICE_FIELDS = ('id', 'createdAt', 'timestamp', 'content', 'senderUserId', 'senderExternalUserId', 'sender',
                 'senderName', 'source')


UNREADABLE_AT = '1970-01-01T00:00:00+00:00'   # unknown time: a fixed value, so every read is the same revision


UNREADABLE_FROM_US = 'us-unreadable'   # author of an unreadable row our company sent: still a hold, and a delivery


def unreadable_msg(r, company_id=None, company_name=None):
    """A row we could not read at all, kept as HER message of kind 'unreadable' with an unidentifiable file: it blocks
    sends and withdrawal until the captain marks it answered and looked at (record.py). Never authorizes anything."""
    rid = r.get('id') if isinstance(r, dict) else None
    if not isinstance(rid, str) or not rid.strip():
        rid = 'unreadable-' + hashlib.sha256(json.dumps(r, sort_keys=True, default=str).encode()).hexdigest()[:16]
    text = r.get('content') if isinstance(r, dict) and isinstance(r.get('content'), str) else ''
    # its identity is its exact payload: the same row read again is the same revision, any change (a new file, new
    # words) is a new one that needs its own marks (review BI01). Not the collapsed 'u-' kind of signature.
    payload = hashlib.sha256(json.dumps(r, sort_keys=True, default=str).encode()).hexdigest()[:16]
    at, edited = UNREADABLE_AT, 'unknown'   # no usable time: its activity time is unknown, i.e. recent (review BT01)
    for field in ('createdAt', 'timestamp'):
        try:
            at, edited = instant(r.get(field)).isoformat(), ''   # a valid creation time is kept, never the placeholder
            break
        except Exception:
            continue
    flag = r.get('isEdited') if isinstance(r, dict) else None   # edit evidence, independently of everything else (BU01)
    if at == UNREADABLE_AT:
        edited = 'unknown'   # no creation time: activity stays unknown whatever the edit says (review BV01)
    elif flag is True:
        edited = usable_revision(r) or 'unknown'
    elif flag is not None and flag is not False:
        edited = 'unknown'
    # still HER unread message for the holds; if our company sent it, it also counts as our delivery (BU02)
    # our company, by the same identity rules as a normal read: our user id, or the bot (no ids, our name) (BV02)
    ours = isinstance(r, dict) and bool(
        (company_id and r.get('senderUserId') == company_id)
        or (not r.get('senderUserId') and not r.get('senderExternalUserId') and company_name
            and (r.get('sender') or r.get('senderName')) == company_name))
    return Msg(id=rid, at=at, edited_at=edited, direction=IN, author=UNREADABLE_FROM_US if ours else 'creator',
               text=text, kind='unreadable',
               attachments=1, attachments_sig='x-' + payload)


def _signing_notice(m):
    return (m.kind == 'handle_request' and m.direction == 'in') or (m.kind == 'handle_approved' and m.direction == 'out')


class SideShiftLive:
    """`client` is integrations/sideshift/client.Client (or a fake with the same `pages`)."""

    def __init__(self, client, company_id, company_name='Excerlock', on_notice=None):
        self.client, self.company_id, self.company_name = client, company_id, company_name
        # on_notice(creator_key, msg): called for each signing notice (her handle request, a SideShift approval) the
        # moment its row is read, before the next page is asked for (review AI01). The gate wires its journal here.
        self.on_notice = on_notice
        self._names = {}   # chat id -> her participant name from the latest membership read (review BP01)

    def members(self, chat_id):
        for conv in self.client.pages('/conversations'):
            if conv.get('id') == chat_id:
                current = tuple(m for m in conv.get('members', []) if m != self.company_id)
                names = [p.get('name') for p in conv.get('participants') or []
                         if isinstance(p, dict) and len(current) == 1 and p.get('id') == current[0]]
                self._names[chat_id] = names[0] if len(names) == 1 and isinstance(names[0], str) else ''
                return current
        raise LiveReadError('ChatNotFound')

    def _notice(self, current, r):
        """Make a signing notice durable as soon as it is read. Only adds evidence (a veto), never permits anything."""
        if self.on_notice is None or not current or len(current) != 1:
            return
        m = self._evidence_msg(r, current)   # every readable message (and rescued notices/invites) (AV01, AY01)
        if m is not None:
            self.on_notice(f'sideshift:{current[0]}', m)

    def _evidence_msg(self, r, current):
        """The message as evidence. If only its other fields are unreadable, its id, sender, time and text still count
        as veto evidence (validated as usual), whatever it says (review AS01, BF01). Media we couldn't read is kept as
        an unidentifiable file, so it needs a look; dropping it never means it was reviewed."""
        try:
            m = to_msg(r, self.company_id, self.company_name, current)
            return m
        except Exception:
            pass
        if not isinstance(r, dict):
            return unreadable_msg(r, self.company_id, self.company_name)   # not even a record: still something we must not lose (BH01)
        core = {k: v for k, v in r.items() if k in NOTICE_FIELDS}
        m = None
        # only a creation field dates a message; an edit time never stands in for it (review BW01)
        for variant in (core, {**core, 'createdAt': core.get('timestamp')}):
            try:   # a broken primary time: a valid alternative time still identifies it (review BH01)
                m = to_msg(variant, self.company_id, self.company_name, current)
                break
            except Exception:
                continue
        if m is None:
            return unreadable_msg(r, self.company_id, self.company_name)   # nothing validates: keep it as an unread message that blocks (BH01)
        edited = r.get('isEdited')   # keep its edit time; a garbled edit flag is an unknown edit, never "unedited" (BR02)
        if edited is True:
            m = replace(m, edited_at=usable_revision(r) or 'unknown')
        elif edited is not None and edited is not False:   # identity, not equality: 0 is not False (review BS01)
            m = replace(m, edited_at='unknown')
        listed, count = r.get('attachments'), r.get('attachmentCount')
        proven_empty = ((listed is None or (type(listed) is list and not listed))   # exact types: False is not 0 (BG01)
                        and (count is None or (type(count) is int and count == 0)))
        if not proven_empty:   # identity from the exact (unreadable) file details: a change needs a new look (BJ01)
            media = json.dumps([listed, count], sort_keys=True, default=str)
            detailed = isinstance(listed, list) and listed and all(isinstance(a, dict) and a for a in listed)
            sig = (PAYLOAD + hashlib.sha256(media.encode()).hexdigest()[:12]) if detailed else (UNIDENTIFIABLE + uuid.uuid4().hex[:12])
            m = replace(m, attachments=max(m.attachments, 1), attachments_sig=sig)
        return m

    def _partial(self, chat_id, current, raws):
        """The messages read before a failure that validate on their own, for signing evidence only (AE02)."""
        if not current or len(current) != 1 or not raws:
            return None
        msgs = []
        for r in raws:
            m = self._evidence_msg(r, current)   # signing notices survive unreadable media fields (AS01)
            if m is not None:
                msgs.append(m)
        if not msgs:
            return None
        order = {id(m): i for i, m in enumerate(msgs)}   # same chronological order as a complete read (AF03)
        msgs.sort(key=lambda m: (instant(m.at), order[id(m)]))
        return Conversation(source='sideshift', external_id=chat_id, creator_ids=current, messages=tuple(msgs),
                            fingerprint='partial', read_at=datetime.now(timezone.utc).isoformat(), complete=False)

    def read(self, chat_id, members=None):
        try:
            current = self.members(chat_id)          # always re-read: membership is part of the evidence
            if members and set(members) != set(current):
                raise LiveReadError('chat members are not the expected creator')
            raws = []
            for r in self.client.pages(f'/support-channels/{chat_id}/messages'):
                raws.append(r)
                self._notice(current, r)
            msgs = [to_msg(r, self.company_id, self.company_name, current) for r in raws]
        except LiveReadError:
            raise
        except Exception as exc:  # transport, API or malformed data: no complete live read
            raise LiveReadError(f'{type(exc).__name__}: {str(exc)[:80]}',
                                self._partial(chat_id, locals().get('current'), locals().get('raws'))) from None
        if not current:
            raise LiveReadError('NoCreatorInChat')
        if len(current) != 1:
            raise LiveReadError('group chat: not exactly one creator')
        if not msgs:
            raise LiveReadError('empty chat history')
        order = {m.id: i for i, m in enumerate(msgs)}   # same time: keep SideShift's own order, never ids (review N27)
        msgs.sort(key=lambda m: (instant(m.at), order[m.id]))
        return Conversation(source='sideshift', external_id=chat_id, creator_ids=current, messages=tuple(msgs),
                            fingerprint=fingerprint(raws, current), read_at=datetime.now(timezone.utc).isoformat(),
                            creator_name=self._names.get(chat_id, ''))
