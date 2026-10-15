"""Withdraw unsigned contract invites after 36 hours, silently (captain, 2026-10-14: no message when withdrawn).

Withdrawing is irreversible for that invite, so every condition must hold, checked fresh right before the call:
  1. the contract is still `pending` in SideShift (fresh GET, not the list from earlier);
  2. the invite is at least 36 hours old;
  3. the live chat shows no handle request (she didn't sign) and no message from her in the last 24 hours
     (2026-10-15: Dakota was actively trying to make accounts at hour 21; never cut off someone who is trying);
  4. nothing from her is waiting for an answer from us;
  5. the captain hasn't said to keep this invite (journal event 'keep-invite');
  6. a SideShift key with contracts:write is configured (SIDESHIFT_CONTRACTS_WRITE_KEY).
If any fails, nothing happens and the reason is journaled for the captain. Every attempt is journaled.
"""
import json
import time
from datetime import timedelta

from gate import checks, clock
from gate.model import IN

WITHDRAW_AFTER = timedelta(hours=36)
RECENT = timedelta(hours=24)
SPAN = 10   # seconds: handle requests, chat and contract must all be read within this window


def blockers(contract_now, conv, now, journal_events, has_write_key, creator_key=None, requested_id=None):
    reasons = []
    contract_now = {**contract_now, 'recorded_invites': checks.recorded_invites(contract_now, journal_events)}   # AT01
    if requested_id is not None and contract_now.get('id') != requested_id:
        reasons.append('SideShift returned a different contract than the one to withdraw')   # review R15
    owner = contract_now.get('contractorId')
    if creator_key and (not owner or f'sideshift:{owner}' != creator_key):
        reasons.append('the contract is not this creator\'s')                  # review N22: identity binding
    if creator_key and (len(conv.creator_ids) != 1 or f'sideshift:{conv.creator_ids[0]}' != creator_key):
        reasons.append('the chat read is not this creator\'s')
    if str(contract_now.get('status') or '').lower() != 'pending':
        reasons.append(f"contract is {contract_now.get('status')}, not pending")
    if checks.invite_order_unclear(conv, contract_now):   # review AW02
        reasons.append('two invites share a time and one is gone from the chat; the captain decides')
    invited = checks.invite_time(conv, contract_now)
    if invited is None:
        reasons.append('no invite time')
    elif now - invited < WITHDRAW_AFTER:
        reasons.append('invite is younger than 36 hours')
    if contract_now.get('applications') is None and contract_now.get('applications_required'):
        reasons.append('her handle requests could not be read from SideShift')                # review R07
    if checks.maybe_accepted(conv, contract_now) or checks.recorded_signing(contract_now, journal_events):   # recorded earlier, even if redacted now (V04)
        reasons.append('she may have signed (handle request or active contract)')
    # her latest content counts from its edit; an unknown edit time counts as recent (review BQ01). Every revision
    # ever observed counts, not only the one that survives in the chat (review BR03)
    recent = [m for m in conv.messages if m.direction == IN
              and (checks.content_time(m) is None or now - checks.content_time(m) < RECENT
                   or now - checks.ts(m.at) < RECENT)]   # a recent creation always counts too (BS02)
    for e in journal_events:
        if e['kind'] != 'msg-seen':
            continue
        try:
            d = json.loads(e['data'])
        except (ValueError, TypeError):
            continue
        if d.get('direction') == IN:
            edited = d.get('edited_at') or ''
            created = checks.ts(d['at'])
            if (edited == 'unknown' or now - created < RECENT   # creation counts on its own; an edit never erases it
                    or (edited and (checks.ts(edited) < created or now - checks.ts(edited) < RECENT))):   # (BS02)
                recent.append(d)
    if recent:
        reasons.append(f'she messaged {len(recent)} time(s) in the last 24 hours; the captain decides')
    answered = checks.valid_answers(journal_events)   # answers that still hold (review CA01)
    looked = {e['ref'] for e in journal_events if e['kind'] == 'attachment-reviewed'}
    if checks.unanswered(conv, answered):
        reasons.append('she is waiting for an answer from us')
    reasons += checks.completeness(conv, looked)
    if any(e['kind'] in ('withdraw-intent', 'withdraw-uncertain', 'withdrawn') and (e['ref'] or '').split(':')[0] == contract_now.get('id')
           for e in journal_events):
        stopped = any(e['kind'] == 'withdraw-not-sent' and e['ref'] == contract_now.get('id') for e in journal_events)
        reasons.append('an earlier withdrawal stopped before sending (nothing was sent); the captain decides' if stopped
                       else 'an earlier withdrawal for this contract was attempted; check SideShift by hand')
    if any(e['kind'] == 'keep-invite' and e['ref'] == contract_now.get('id') for e in journal_events):
        reasons.append('the captain said to keep this invite')
    if not has_write_key:
        reasons.append('no SideShift key with contracts:write is configured')
    return reasons


REJECTED = {'rejected', 'cancelled', 'canceled', 'declined', 'ended'}


def withdraw(contract_id, fetch_contract, read_chat, journal, creator_key, now, write_client=None, read_applications=None,
             started=None):
    """Returns ('withdrawn'|'held', reasons). fetch_contract(id) must do a fresh GET; read_chat() a live read;
    read_applications() a fresh read of her handle requests (None when no read key is configured).
    started: when the caller's own evidence (her contacts identity) was first read; the window counts from then (CW01)."""
    started = clock.Since() if started is None else started   # counts sleep too (DA01)

    def apps_now():
        try:
            return read_applications() if read_applications is not None else None   # no reader = unknown (S02)
        except Exception:
            return None
    def observe(apps, contract=None, chat=True):   # positive evidence is kept the moment it is read (Y03, Z01, AA01)
        probe = {**(contract or {}), 'id': contract_id, 'applications': apps or []}
        seen = checks.signing_seen(conv, probe) if chat else bool(checks.structured_requests(probe))
        if seen and contract_id not in journal.flags(creator_key, 'maybe-signed'):
            journal.event(creator_key, 'maybe-signed', contract_id, {'by': 'withdraw'})

    applications = apps_now()
    try:
        conv = read_chat()
    except Exception as exc:
        observe(applications, chat=False)   # no chat to place it in a round: any request she made counts (AA01)
        if getattr(exc, 'partial', None) is not None:   # a notice read before the failure counts too (AE02)
            conv = exc.partial
            observe(applications)
        raise
    observe(applications)
    journal.remember_invites(creator_key, contract_id, checks.invite_links(conv, {'id': contract_id}))   # AV01
    contract_now = fetch_contract(contract_id)   # after the chat: nothing slow between it and the decision (S03)
    if not isinstance(contract_now, dict):
        return 'held', ['the contract could not be re-read']
    if contract_now.get('id') == contract_id and f"sideshift:{contract_now.get('contractorId')}" == creator_key:
        observe(applications, contract_now)   # e.g. now active: durable before the next (possibly slow) read
    again = apps_now()
    observe(again, contract_now)   # an active contract is positive evidence too
    # her handle requests once more, last; they must not have changed meanwhile (W01)
    if applications is None or again is None or again != applications:
        applications = None if again != applications else applications
    if started.age() > SPAN:
        applications = None   # reads too far apart: treat signing evidence as unknown
    contract_now = {**contract_now, 'applications': applications, 'applications_required': True}
    if len(journal.component_accounts(creator_key)) > 1:   # several linked accounts: the captain decides (CU01)
        journal.event(creator_key, 'withdraw-held', f'{contract_id}:{now:%Y-%m-%dT%H}',
                      {'reasons': ['she has other linked SideShift accounts; the captain decides']})
        return 'held', ['she has other linked SideShift accounts; the captain decides']
    for m in conv.messages:   # every revision read, then decide on everything ever seen (review AY01)
        journal.remember_message(creator_key, m)
    events = journal.events(creator_key)
    reasons = blockers(contract_now, checks.with_history(conv, events), now, events, write_client is not None, creator_key, contract_id)
    if reasons:
        journal.event(creator_key, 'withdraw-held', f'{contract_id}:{now:%Y-%m-%dT%H}', {'reasons': reasons})
        return 'held', reasons
    if not journal.event(creator_key, 'withdraw-intent', contract_id, {'at': now.isoformat()}):   # one owner, ever (R15)
        return 'held', ['another withdrawal of this contract is already in progress or done']
    if started.age() > SPAN:   # the intent write waited on the database: evidence too old (Z02)
        journal.event(creator_key, 'withdraw-not-sent', contract_id, {'why': 'checks went stale before the request'})
        return 'held', ['the checks went stale before the withdrawal request; nothing was sent, the captain decides']
    try:
        result = write_client.request('POST', f'/contracts/{contract_id}/reject', payload={}, request_id=f'withdraw-{contract_id}')
    except Exception as exc:  # may or may not have happened: record, never retry
        journal.event(creator_key, 'withdraw-uncertain', contract_id, {'error': type(exc).__name__})
        return 'held', [f'withdraw call failed ({type(exc).__name__}); check SideShift before doing anything else']
    data = result.get('data', result) if isinstance(result, dict) else {}
    if (str((data or {}).get('status', '')).lower() not in REJECTED or data.get('id') != contract_id
            or (data.get('contractorId') and f"sideshift:{data['contractorId']}" != creator_key)):   # review S04
        journal.event(creator_key, 'withdraw-uncertain', contract_id, {'response': str(result)[:200]})
        return 'held', ['SideShift did not confirm the withdrawal; check by hand']
    journal.event(creator_key, 'withdrawn', contract_id, {'at': now.isoformat(), 'silent': True})
    return 'withdrawn', ['36 hours without signing; no message sent']
