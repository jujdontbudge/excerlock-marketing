"""Deterministic vetoes. Each returns a list of reasons; any reason means: do not send.

Pure functions over the live conversation, the action, journal facts and `now`.

Signing has two levels (review G09, 2026-10-15):
- `maybe_accepted`: a handle request from her in this chat after THIS contract's latest invite. Chat text can be typed
  by anyone, so it can only STOP things (reminders, withdrawal), never start onboarding.
- `accepted`: positive proof only: the contract is `active` in SideShift (or structured application data, once we can
  read it). Only this starts onboarding ("welcome", "send your email").
"""
import json
import re
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .live import REQUEST_NOTICE_EXACT, classify, content_sha, instant, invite_contract_id, revision_key
from .model import IN, OUT, UNKNOWN, Msg

EASTERN = ZoneInfo('America/New_York')
WINDOW = (9, 21)  # 09:00 inclusive to 21:00 exclusive, US Eastern (captain, 2026-10-14)
INVITE_TTL = timedelta(hours=24)   # invites close 24h after they're sent (captain, 2026-10-15; was 36h)
INVITE_AGE = {'invite_6h': 6, 'invite_12h': 12}   # reminder schedule: hours since the current invite (review AJ03)
SYSTEM_KINDS = {'handle_request', 'handle_approved', 'invite_link', 'system'}
ONBOARDING_STATUSES = {'active'}
CLOSED_STATUSES = {'cancelled', 'canceled', 'rejected', 'declined', 'expired', 'ended', 'completed'}


def ts(value):
    return instant(value)


def status(contract):
    return str((contract or {}).get('status') or '').lower()


REPOST_WINDOW = timedelta(hours=1)


def invite_row(m):
    """An invite we sent: a readable outbound invite link, or an unreadable row from us whose words are one (its
    other fields being garbled doesn't undo the delivery) (review BX01)."""
    if m.kind == 'unreadable':
        return m.author == 'us-unreadable' and classify(m.text or '') == 'invite_link'
    return m.direction == OUT and m.kind == 'invite_link'


def invite_links(conv, contract):
    """Invite links WE sent for exactly this contract that start an invite round. Right after SideShift approves one
    of her handles ("✅ Your handle … was approved", posted by SideShift, never typed by her) it re-posts the invite
    link; a link within an hour after such an approval is that repost, even with other messages in between
    (review N16). A link later than that is a genuine new invite (review R16)."""
    cid = (contract or {}).get('id')
    if not cid:
        return []
    out, last_approval = [], None
    for m in conv.messages:   # deleted rows count: deleting a message never undoes its delivery (review AT01)
        if m.direction == OUT and m.kind == 'handle_approved':
            last_approval = content_time(m)   # None (unknown) can't make anything a repost (review CK01)
        elif invite_row(m) and invite_contract_id(m.text) == cid:
            ct = content_time(m)   # when THIS link appeared, not when the row was created (review CK01)
            if last_approval is None or ct is None or not (timedelta(0) <= ct - last_approval <= REPOST_WINDOW):
                out.append(m)
    # genuine invites seen on earlier reads stay, even if the row later vanishes entirely (AT01)
    seen = {m.id for m in out}
    for r in (contract or {}).get('recorded_invites') or []:
        if r.get('id') not in seen:
            out.append(Msg(id=r['id'], at=r.get('created') or r['at'],
                           edited_at='unknown' if r.get('unknown') else (r['at'] if r.get('edited') else ''),
                           direction=OUT, author='company', kind='invite_link', deleted=True,
                           text=f'https://app.sideshift.app/campaign-invite/{cid}'))
    return sorted(out, key=lambda m: ts(m.at))


def invite_order_unclear(conv, contract):
    """A remembered invite missing from the chat shares its time with another invite: which one came last (the current
    round) can't be known, so automation holds for the captain rather than guess (review AW02)."""
    links = invite_links(conv, contract)
    if not links:
        return False
    # an invite counts as live only while its row still carries the invite itself; a blanked row is reconstructed (AX01)
    cid = (contract or {}).get('id')
    intact = {m.id for m in conv.messages if m.kind == 'invite_link' and m.direction == OUT and not m.vanished
              and invite_contract_id(m.text) == cid}   # this contract's invite, live (review AY02)
    gens = {}   # one entry per invite generation (an edited-in invite is its own), deduplicated (review BU03)
    for m in links:
        gens.setdefault(m.id if not m.edited_at else f'{m.id}@{m.edited_at}', m)
    times = {g: content_time(m) for g, m in gens.items()}
    if any(t is None for t in times.values()):
        return True   # timing unknown: which invite is current can't be known (BQ01)
    latest = max(times.values())
    tied = [gens[g] for g, t in times.items() if t == latest]   # only a tie at the LATEST time matters (AX03)
    return len(tied) > 1 and any(m.id not in intact for m in tied)


def invite_time(conv, contract=None):
    """When the current invite round started: the latest real invite link we sent. Never guessed from creation times."""
    links = invite_links(conv, contract)
    times = [content_time(m) for m in links]
    if not links or any(t is None for t in times):   # an edit with an unusable time: no clock, automation holds (BQ01)
        return None
    return max(times)


_WORDS = {w: i for i, w in enumerate('zero one two three four five six seven eight nine ten eleven twelve thirteen '
                                     'fourteen fifteen sixteen seventeen eighteen nineteen twenty'.split())}
_WORDS.update({'a': 1, 'an': 1, 'twenty-four': 24, 'twenty four': 24, 'thirty': 30, 'thirty-six': 36,
               'forty-eight': 48, 'a couple of': 2, 'couple of': 2, 'a few': 3, 'few': 3})
_NUM = r'(\d+|' + '|'.join(sorted((re.escape(w) for w in _WORDS), key=len, reverse=True)) + r')'
_UNIT = r'(hours?|hrs?|days?)'
_PROMISE = [re.compile(r'\b' + _NUM + r'\s+(?:more|additional|extra)\s+' + _UNIT + r'\b', re.I),
            re.compile(r'\b(?:another|next|the next)\s+' + _NUM + r'\s+' + _UNIT + r'\b', re.I)]
_CLOSING = re.compile(r'\b(clos(e|es|ed|ing)|expir\w*|withdraw\w*|deadline|last chance|stays? open|keep (?:your|the) (?:invite|spot|contract) open)\b', re.I)
UNKNOWN_SPAN = timedelta.max   # closing words without a duration we can read: the captain decides (review DJ01)


def promised_open(text):
    """How long a message of ours promised the invite stays open ("open for 12 more hours", "twelve more hours",
    "about one more day", "another 12 hrs"), as a timedelta; UNKNOWN_SPAN when it talks about closing or staying open
    but no duration can be read; None when it promises nothing. Any wording counts, the captain's own too (DI01, DJ01)."""
    spans = []
    for pattern in _PROMISE:
        for n, unit in pattern.findall(text or ''):
            count = int(n) if n.isdigit() else _WORDS[n.lower()]
            spans.append(timedelta(hours=count * (24 if unit.lower().startswith('d') else 1)))
    if spans:
        return max(spans)
    return UNKNOWN_SPAN if _CLOSING.search(text or '') else None


def content_time(m):
    """When a message's CURRENT content appeared: its edit time if edited, else its creation time. None when it was
    edited but the time is unusable, so clocks built on it hold (review BQ01)."""
    if m.edited_at == 'unknown':
        return None
    if not m.edited_at:
        return ts(m.at)
    edited = ts(m.edited_at)
    return None if edited < ts(m.at) else edited   # an edit before creation is contradictory: unknown (BS02)


def invite_generation(conv, contract):
    """Identifies one invite round, so a re-invite gets fresh reminder keys (review G10). The round is the invite whose
    link appeared last (an edited-in link counts from its edit, BQ01); unknown timing gives no round."""
    links = invite_links(conv, contract)
    times = [content_time(m) for m in links]
    if not links or any(t is None for t in times):
        return None
    latest = max(times)
    m = [m for m, t in zip(links, times) if t == latest][-1]
    return m.id if not m.edited_at else f'{m.id}@{m.edited_at}'   # an edited-in invite is its own round (BT03)


def structured_requests(contract, since=None, eligible_only=False):
    """Her handle requests for this campaign from SideShift's own records (attached by the flow as
    contract['applications']), pending or approved, made in the current invite round."""
    out = []
    for a in (contract or {}).get('applications') or []:
        if not isinstance(a, dict):
            out.append({'status': 'unknown'})   # unreadable record: possibly signed
            continue
        if eligible_only and str(a.get('status') or '').lower() not in ('pending', 'approved'):
            continue   # for handle checks only; as signing EVIDENCE every request counts, whatever happened later (U01, V04)
        try:
            at = ts(a.get('requestedAt'))
        except ValueError:
            at = None
        if since is None or at is None or at >= since:
            out.append(a)
    return out


def first_invite_time(conv, contract=None):
    cid = (contract or {}).get('id')
    # deleted invites count: deleting the original must never move signing's lower bound forward (review AH01)
    links = [m for m in conv.messages if m.direction == OUT and m.kind == 'invite_link'
             and invite_contract_id(m.text) == cid] if cid else []
    return ts(links[0].at) if links else None


def maybe_accepted(conv, contract=None):
    """Any sign she may have signed this contract, ever since its FIRST invite (review S01: re-posts, delayed re-posts
    and re-invites can never erase it). Blocks reminders and withdrawal; never starts onboarding.
    Sources: active contract; her requests in SideShift's records; unknown records when they are required (S02);
    a handle-request notice from her; a SideShift handle approval in the chat."""
    if signing_seen(conv, contract) or (contract or {}).get('signing_recorded'):
        return True   # signing_recorded: the journal saw positive evidence earlier; a later redaction can't erase it (V04)
    # unknown is not "none": treat as possibly signed, but it is never recorded as signing evidence
    return bool((contract or {}).get('applications_required') and (contract or {}).get('applications') is None)


def signing_notice(m):
    """A handle request from her or a SideShift approval from us, or an unreadable row whose words are one of those
    notices: its other fields being garbled doesn't undo it. Signing evidence only ever adds a veto (review BW02)."""
    if m.kind == 'unreadable':
        return classify(m.text or '') in ('handle_request', 'handle_approved')
    return (m.kind == 'handle_request' and m.direction == IN) or (m.kind == 'handle_approved' and m.direction == OUT)


def _before(m, since):
    """Provably before `since`: created AND (if edited) its current content appeared before it. An unknown edit time
    is never proof (review BR01)."""
    if since is None:
        return False
    ct = content_time(m)
    return ct is not None and ts(m.at) < since and ct < since


def signing_seen(conv, contract=None):
    """POSITIVE evidence only (no unknowns): active contract, her request in SideShift's records, a handle-request
    notice from her, or a SideShift handle approval, since the first invite. This is what the journal records as
    'maybe-signed', so it outlives a deleted or redacted notice (review V04)."""
    if status(contract) in ONBOARDING_STATUSES:
        return True
    # an incomplete history may be missing the real first invite, so it can't place anything before it (AG01)
    since = first_invite_time(conv, contract) if getattr(conv, 'complete', True) else None
    if structured_requests(contract, since):
        return True
    return any(signing_notice(m)
               and not _before(m, since) for m in conv.messages)   # deleted notices still count (V04)


def name_matches(action, conv=None):
    """A message that greets her by name needs POSITIVE current evidence of that name from SideShift: her contract's
    name and/or her name on the chat as read now. Every available one must match; none available holds (AL02, BP01)."""
    first = (action.fields or {}).get('First')
    if first is None:
        return []
    names = [n for n in ((action.contract or {}).get('contractorName'), getattr(conv, 'creator_name', ''))
             if isinstance(n, str) and n.strip()]
    if not names:
        return ['no current name from SideShift to check the greeting against']
    for n in names:
        if first.strip().lower() != n.split(' ')[0].strip().lower():
            return [f'the name in the message ({first}) is not her name in SideShift ({n.split(" ")[0]})']
    return []


def unexplained_changes(events):
    """Message ids whose words were SEEN to change without a believable edit time: the new words' claimed time (edit
    time, else creation) is missing, unknown or earlier than when we last saw the old words. For those, every clock
    built on the message (invite age, signing dates, activity) is unknown, so nothing relies on it (review CH01)."""
    seen, last = {}, {}
    for e in events:
        if e['kind'] == 'msg-last':   # the latest read of a revision (review CI01)
            try:
                last[e['ref']] = ts(e['at'])
            except (ValueError, TypeError):
                pass
    for e in events:
        if e['kind'] != 'msg-seen':
            continue
        try:
            d = json.loads(e['data'])
            rev = str(e['ref']).split('@seen', 1)[0]
            read_at = max(ts(e['at']), last.get(rev, ts(e['at'])))
            # exact words, not whitespace-normalised: one space can turn plain text into a signing notice (CJ01)
            sig = d.get('attachments_sig') or ''
            sig = 'u-' if sig.startswith('u-') else sig   # a refreshed per-read signature is not a new file
            content = (d.get('text') or '', int(d.get('attachments') or 0), sig)   # words AND files (review CL01)
            seen.setdefault(d['id'], []).append((e['id'], read_at, content,
                                                 d.get('edited_at') or '', d.get('at')))
        except (ValueError, TypeError, KeyError):
            continue
    bad = set()
    for mid, rows in seen.items():
        rows.sort()
        for (_, prev_at, prev_text, _, _), (_, _, text, edited, created) in zip(rows, rows[1:]):
            if text == prev_text or not (text[0].strip() or text[1]):
                continue   # unchanged, or blanked (no new words appeared, so no new clock is needed)
            try:
                claim = None if edited == 'unknown' else ts(edited or created)
            except (ValueError, TypeError):
                claim = None
            if claim is None or claim < prev_at:
                bad.add(mid)
    return bad


def with_history(conv, events):
    """The live chat plus every message revision seen on earlier reads that is no longer there in that form
    ('msg-seen'). A revision of a message still in the chat is added as deleted (it was delivered, then changed); a
    message gone from the chat is added as it was (she may still be waiting on it). Evidence can only be added, so
    anything that later vanishes upstream can only add reasons to hold (review AY01-AY04)."""
    live_keys = {revision_key(m) for m in conv.messages}
    # only a visible row from the SAME sender supersedes an older revision: a tombstone or a changed sender settles
    # nothing (review BB03, BC01)
    live_rows = {(m.id, m.direction, m.author, ts(m.at)) for m in conv.messages if not m.deleted}
    extra, seen = [], set()
    for e in events:
        if e['kind'] != 'msg-seen':
            continue
        try:
            d = json.loads(e['data'])
            old = Msg(id=d['id'], at=d['at'], direction=d['direction'], author=d['author'], text=d.get('text') or '',
                      kind=d.get('kind') or 'text', deleted=bool(d.get('deleted')),
                      attachments=int(d.get('attachments') or 0), attachments_sig=d.get('attachments_sig') or '',
                      edited_at=d.get('edited_at') or '', vanished=True)
            k = revision_key(old)
            if k in live_keys or k in seen:
                continue
            seen.add(k)
            # an older revision of a row still present was delivered then changed: kept as deleted, EXCEPT a file she
            # added that nobody looked at, which keeps blocking until reviewed (AZ01)
            unseen_file = old.attachments and old.direction == IN
            superseded = (old.id, old.direction, old.author, ts(old.at)) in live_rows and not unseen_file   # same time too (BB01)
            if superseded and old.direction == IN and old.kind == 'text':   # a signing notice is never superseded (BO01)
                continue   # her own visible edit replaced it: the current version carries what she needs (BD01)
            extra.append(replace(old, deleted=old.deleted or superseded))
        except (ValueError, TypeError, KeyError):
            continue
    bad = unexplained_changes(events)   # their clocks prove nothing (review CH01)
    if bad:
        extra = [replace(m, edited_at='unknown') if m.id in bad else m for m in extra]
        live_msgs = [replace(m, edited_at='unknown') if m.id in bad else m for m in conv.messages]
        conv = replace(conv, messages=tuple(live_msgs))
    if not extra:
        return conv
    msgs = list(conv.messages) + extra
    order = {id(m): i for i, m in enumerate(msgs)}
    msgs.sort(key=lambda m: (ts(m.at), order[id(m)]))
    return replace(conv, messages=tuple(msgs))


def evidence_digest(conv):
    """Every message revision in a (history-merged) chat: what a review saw. If it changes, the review is stale (BD02)."""
    return content_sha('|'.join(sorted(revision_key(m) for m in conv.messages)))


def recorded_invites(contract, events):
    """Genuine invites for this contract seen on earlier reads ('invite-seen'), as {id, at} (review AT01)."""
    cid = (contract or {}).get('id')
    out, approvals = [], []
    bad = unexplained_changes(events)
    for e in events:
        try:
            d = json.loads(e['data'])
        except (ValueError, TypeError):
            continue
        if e['kind'] == 'notice-seen' and d.get('kind') == 'handle_approved' and d.get('at'):
            approvals.append(ts(d['at']))
        elif (e['kind'] == 'invite-seen' and d.get('contract') == cid and d.get('id') and d.get('at')
              and d.get('direction') == 'out'):   # delivery provenance required; anything else is not our invite (BC02)
            out.append({'id': d['id'], 'at': d['at'], 'edited': bool(d.get('edited')), 'created': d.get('created') or d['at'],
                        'unknown': d['id'] in bad})   # its time can't be trusted (review CH01)
    # SideShift's automatic re-post right after a handle approval is not a new invite (same rule as invite_links)
    return [r for r in out if not any(timedelta(0) <= ts(r['at']) - a <= REPOST_WINDOW for a in approvals)]


def recorded_signing(contract, events):
    """Signing evidence already in the journal for this contract: a 'maybe-signed' fact for it, or a handle request
    of hers recorded the moment it was read ('request-seen') that is not provably older than the contract. Read from
    the journal, so neither a redacted notice nor a failed page can erase it (V04, AG02)."""
    cid = (contract or {}).get('id')
    try:
        created = ts(contract.get('createdAt')) if (contract or {}).get('createdAt') else None
    except ValueError:
        created = None
    bad = unexplained_changes(events)   # a notice on a message whose clock can't be trusted always counts (CH01)
    for e in events:
        if e['kind'] == 'maybe-signed' and e['ref'] == cid:
            return True
        if e['kind'] == 'notice-seen' and str(e['ref']).split('@', 1)[0] in bad:
            return True
        if e['kind'] == 'msg-seen':   # a signing notice kept as a message revision counts too (review BO01)
            try:
                data = json.loads(e['data'])
            except (ValueError, TypeError):
                continue
            notice = ((data.get('kind') == 'handle_request' and data.get('direction') == IN)
                      or (data.get('kind') == 'handle_approved' and data.get('direction') == OUT)
                      or (data.get('kind') == 'unreadable'
                          and classify(data.get('text') or '') in ('handle_request', 'handle_approved')))   # (BW02)
            if not notice:
                continue
            edited = 'unknown' if data.get('id') in bad else (data.get('edited_at') or '')   # (BR01, CH01)
            e = {'kind': 'notice-seen', 'data': json.dumps({'at': None if edited == 'unknown' else (edited or data.get('at'))})}
        if e['kind'] in ('request-seen', 'notice-seen'):
            try:
                data = json.loads(e['data'])
                at = data.get('requestedAt') if e['kind'] == 'request-seen' else data.get('at')
                if created is None or not at or ts(at) >= created:
                    return True
            except (ValueError, TypeError, AttributeError):
                return True
    return False


def accepted(conv, contract=None):
    """Positive proof she signed: the contract is active in SideShift."""
    return status(contract) in ONBOARDING_STATUSES


def contract_open(conv, contract, now):
    if status(contract) != 'pending':
        return False
    invited = invite_time(conv, contract)
    return invited is not None and now - invited < INVITE_TTL


STATE = {
    'contract_open': lambda conv, a, now: contract_open(conv, a.contract, now),
    'not_accepted': lambda conv, a, now: not maybe_accepted(conv, a.contract),
    'accepted': lambda conv, a, now: accepted(conv, a.contract),
    'contract_active': lambda conv, a, now: status(a.contract) == 'active',
    **{name: (lambda h: lambda conv, a, now: (invite_time(conv, a.contract) is not None
                                             and now - invite_time(conv, a.contract) >= timedelta(hours=h)))(hours)
       for name, hours in INVITE_AGE.items()},
}


def state(conv, action, requires, now=None):
    now = now or datetime.now(timezone.utc)
    reasons = []
    for name in requires:
        test = STATE.get(name)
        if test is None:
            reasons.append(f'unknown state requirement {name}')
        elif not test(conv, action, now):
            reasons.append(f'state: {name} is false')
    return reasons


def binding(conv, action):
    """The chat we read must be exactly this creator's one-to-one chat, and the contract must be hers (review G01)."""
    reasons = []
    if len(conv.creator_ids) != 1:
        reasons.append('chat is not one-to-one with exactly one creator')
    elif action.creator_key != f'sideshift:{conv.creator_ids[0]}':
        reasons.append('the chat read is not this creator\'s chat')
    if conv.external_id != action.source_chat_id:
        reasons.append('read a different chat than the action names')
    if action.contract:
        contractor = action.contract.get('contractorId')
        if not contractor:
            reasons.append('the contract does not say whose it is')   # positive binding only (review N10)
        elif f'sideshift:{contractor}' != action.creator_key:
            reasons.append('the contract belongs to someone else')
    return reasons


def mark(m):
    """The token a mark must carry to cover this exact message: its id plus a fingerprint of what it said (review N12)."""
    return f'{m.id}#{content_sha(m.text)}#{m.attachments}' + (f'#{m.attachments_sig}' if m.attachments_sig else '')


def answer_mark(m):
    """The token an ANSWER must carry: the content mark plus its edit, so an edited (or edited-and-restored) message
    needs a fresh answer. Unedited messages keep exactly their old token (review BZ01)."""
    return mark(m) + (f'~{m.edited_at}' if m.edited_at else '')


def valid_answers(events):
    """Answer tokens that still hold. An answer stops counting once its message was seen in ANY other form after it
    (an edit, a blank, a change that later came back): returning to old words never restores an old answer, even when
    the source gives no usable edit time (review CA01). Old answer facts (ref = token) are read too."""
    answers, seen = [], []
    for e in events:
        if e['kind'] == 'answered':
            try:
                d = json.loads(e['data'])
            except (ValueError, TypeError):
                d = {}
            # valid from what the answer was GIVEN for: a reply counts from its review, not its late result (CB01)
            since = d.get('since') if isinstance(d.get('since'), int) else e['id']
            answers.append((since, d.get('token') or e['ref']))
        elif e['kind'] == 'msg-seen':
            try:
                d = json.loads(e['data'])
                m = Msg(id=d['id'], at=d['at'], direction=d['direction'], author=d['author'], text=d.get('text') or '',
                        kind=d.get('kind') or 'text', deleted=bool(d.get('deleted')),
                        attachments=int(d.get('attachments') or 0), attachments_sig=d.get('attachments_sig') or '',
                        edited_at=d.get('edited_at') or '')
            except (ValueError, TypeError, KeyError):
                continue
            seen.append((e['id'], m.id, answer_mark(m)))
    valid = set()
    for aid, token in answers:
        mid = token.split('#', 1)[0]
        if not any(sid > aid and smid == mid and stok != token for sid, smid, stok in seen):
            valid.add(token)
    return valid


def completeness(conv, reviewed_attachments=()):
    reasons = [f'message {m.id} has an unknown sender' for m in conv.messages if m.direction == UNKNOWN]
    # deleted ones too: a file she sent was delivered, deletion is not a review (review BD01)
    unseen = [m for m in conv.messages if m.direction == IN and m.attachments and mark(m) not in reviewed_attachments]
    # a file with nothing to identify it ('u-'): no look can ever prove which file was seen, so it always holds;
    # the captain handles that creator by hand (review AN01, BK01)
    unseen += [m for m in conv.messages if m.direction == IN and m.attachments and m.attachments_sig.startswith('u-')
               and m not in unseen]
    if unseen:
        reasons.append(f'she sent {len(unseen)} attachment(s) nobody has marked as looked at')
    return reasons


def quiet_hours(now):
    local = now.astimezone(EASTERN)
    return [] if WINDOW[0] <= local.hour < WINDOW[1] else [f'outside 9am–9pm Eastern ({local:%H:%M} ET)']


APPROVAL_EXACT = re.compile(r'✅ Your handle @[^\s?]+ on (tiktok|instagram) was approved for [^\n?]+\. '
                            r'(Your contract has been automatically accepted\.|You can now accept the contract\.)')


def gap_exempt(m):
    """SideShift's OWN automatic notices, by exact shape: a bare invite link or an exact handle-approval notice from the
    company bot. Anything else we send counts for the gap, whatever it starts with (review CE01, CK02)."""
    if m.direction != OUT or m.author != 'company' or m.attachments:   # a file is extra content, never exempt (CM01)
        return False
    if m.kind == 'invite_link':
        return True
    return m.kind == 'handle_approved' and bool(APPROVAL_EXACT.fullmatch((m.text or '').strip()))


def min_gap(conv, now, minutes, local_sends=()):
    """`local_sends`: times of sends the journal knows about, in case SideShift hasn't shown them yet (review G06)."""
    if minutes <= 0:
        return []
    # deleted deliveries count: deleting a message doesn't undo that she got it (review AW01)
    # only SideShift's own automatic notices are exempt; anything the captain wrote counts, whatever it starts with (CE01)
    ours = [m for m in conv.messages if m.direction == OUT and not gap_exempt(m)]
    outs = [ts(m.at) for m in ours]
    # an edit is activity too; an unknown or contradictory edit time counts as just now (review BT02)
    outs += [content_time(m) or now for m in ours if m.edited_at]
    for m in conv.messages:   # an unreadable row our company sent is still our delivery (review BU02)
        if m.author == 'us-unreadable':
            outs += [ts(m.at), content_time(m) or now]
    outs += list(local_sends)
    if outs and now - max(outs) < timedelta(minutes=minutes):
        ago = max(0, int((now - max(outs)).total_seconds() // 60))   # a future time (clock skew) counts as just now
        return [f'we messaged this chat {ago} min ago (min gap {minutes})']
    return []


def unanswered(conv, answered=()):
    """Her text messages not explicitly settled. A message is settled only by a mark that covers its exact content
    ('answered' event, from the captain via record.py, or from a gate reply whose full-chat review confirmed it
    answered everything). Writing something after it, even the captain, is not proof (review G13/N13)."""
    # deleted ones too, while still readable: deletion is not an answer (review BD01)
    return [m for m in conv.messages if m.direction == IN and (m.text.strip() or m.attachments) and answer_mark(m) not in answered
            and not (m.kind == 'handle_request' and REQUEST_NOTICE_EXACT.fullmatch(m.text.strip()))]   # (AN02)


def newer_than_captain(conv, messages):
    """The ones written after the captain's last message: nobody has looked at them at all yet."""
    last = max((ts(m.at) for m in conv.messages if m.direction == OUT and m.author == 'captain' and not m.deleted), default=None)
    return [m for m in messages if last is None or ts(m.at) > last]


EMAIL_EXACT = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}', re.ASCII)


WRAPPERS = (('<', '>'), ('(', ')'), ('[', ']'), ('"', '"'), ("'", "'"), ('`', '`'), ('“', '”'), ('‘', '’'))


def email_tokens(text):
    """Every whole email-like token in a message, lowercased: what she actually wrote, never a suffix of something
    longer (alias%ada@x.com is not ada@x.com) (review BA02)."""
    out = set()
    for tok in (text or '').split():   # whitespace only: punctuation INSIDE a word stays part of it (BB02)
        tok = tok.rstrip('.,;:!?')   # sentence punctuation may follow an address; nothing is cut in front (BE01)
        for left, right in WRAPPERS:   # only a matched pair around the WHOLE address is removed
            if len(tok) > 2 and tok.startswith(left) and tok.endswith(right):
                tok = tok[len(left):-len(right)].rstrip('.,;:!?')
                break
        if EMAIL_EXACT.fullmatch(tok):   # validated AS WRITTEN (ASCII only), then lowercased (review BF02)
            out.add(tok.lower())
    return out


def text_digest(text):
    """Fingerprint of a message's words, ignoring spacing: what a duplicate check compares (review AX02)."""
    return content_sha(' '.join((text or '').split()))


def changed_messages(events):
    """Message ids whose words were seen to change (more than one distinct text observed): their dates can't prove
    when the current words appeared (review CG01)."""
    texts = {}
    for e in events:
        if e['kind'] != 'msg-seen':
            continue
        try:
            d = json.loads(e['data'])
            texts.setdefault(d['id'], set()).add(d.get('text') or '')   # exact words (CJ01)
        except (ValueError, TypeError, KeyError):
            continue
    return {i for i, t in texts.items() if len(t) > 1}


def already_in_chat(conv, text, since=None, changed=()):
    """The exact words were already delivered (deleted ones too, AW01; our unreadable rows too, BV03). With `since`
    (a per-invite message), only deliveries not provably before that invite round count (review CF01)."""
    norm = ' '.join(text.split())
    return any((m.direction == OUT or m.author == 'us-unreadable') and ' '.join(m.text.split()) == norm
               and not (since is not None and m.id not in changed   # words that changed prove nothing old (CG01)
                        and content_time(m) is not None and ts(m.at) < since and content_time(m) < since)
               for m in conv.messages)


def before_round(d, since, changed=()):
    """A journaled delivery (out-seen data) provably sent, and not edited, before `since`."""
    if since is None or d.get('id') in changed or not d.get('id'):
        return False   # words seen to change, or a legacy fact without its message id: not provably old (CG01)
    try:
        created = ts(d['at'])
        edited = d.get('edited_at') or ''
        if edited == 'unknown':
            return False
        return created < since and (not edited or ts(edited) < since)
    except (KeyError, ValueError, TypeError):
        return False
