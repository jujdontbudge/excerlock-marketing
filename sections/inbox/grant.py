"""Give a signed creator free ExcerLock Premium for the email she gave us (captain, 2026-10-14), and record it.

Follows ~/.claude/skills/excerlock-access/SKILL.md: exact email, a useful note, `check` before granting, grant once,
and on any unclear result `check` again instead of retrying. Only a successful run whose GRANTED/ACTIVE line names
exactly this email counts (review N25). A durable 'grant-intent' gives one owner per creator and email; if an earlier
attempt never confirmed, we only `check` and leave the rest to the captain (review N26). The confirmed result is
journaled as 'premium-granted', which is what lets the `app-access` message go out. Nothing is sent to the creator.
In the gate this runs as the last step before an app-access send, after every other check passed (review N02).
"""
import re
import subprocess


def _guard():
    try:
        from gate.dispatch import GRANT_GUARD
    except Exception:
        return None
    return GRANT_GUARD.get()

def _since():
    from gate.clock import Since
    try:
        from gate.dispatch import GRANT_WALL
        wall = GRANT_WALL.get()
    except Exception:
        wall = None
    return Since(wall)

def _span():
    from gate.dispatch import EVIDENCE_SPAN
    return EVIDENCE_SPAN


EMAIL = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$')


def _run(args, runner):
    """First output line of `excerlock-access <args>`; any failure becomes an ERROR line, never an exception."""
    try:
        out = runner(['excerlock-access', *args], capture_output=True, text=True, timeout=60)
    except Exception as exc:
        return [f'ERROR: {type(exc).__name__}']
    if getattr(out, 'returncode', 0) != 0:
        return [f"ERROR: exit {out.returncode}: {((out.stderr or out.stdout or '').strip().splitlines() or [''])[0][:160]}"]
    return (out.stdout or '').strip().splitlines()[0:1] or ['ERROR: no output']


def _names(line, word, email):
    """'WORD: <exactly this email> …': the status word with a colon, then the very first token is the email (R13)."""
    m = re.match(rf'^{word}: (\S+)', line or '')
    return bool(m) and m.group(1).lower().rstrip('.') == email


def active(email, runner=subprocess.run):
    """READ-ONLY: True only when `excerlock-access check` says Premium is active for exactly this email now."""
    email = (email or '').strip().lower()
    return bool(EMAIL.match(email)) and _names(_run(['check', email], runner)[0], 'ACTIVE', email)


def grant(journal, creator_key, email, note, runner=subprocess.run):
    """Returns (ok, line). ok only when Premium is confirmed active for exactly this email."""
    email = (email or '').strip().lower()
    if not EMAIL.match(email):
        return False, 'not an email'
    if {by for by, _ in journal.premium_owners(email)} - {creator_key}:   # early exit; re-checked atomically below
        return False, 'this Premium account already belongs to another creator; the captain decides'   # review W04
    if journal.creator_premium_emails(creator_key) - {email}:   # early exit; re-checked atomically below (CX01)
        return False, 'she already has (or an attempt claimed) Premium on another email; a change is for the captain'
    checked_at = _since()   # the check's answer is evidence from BEFORE it ran: its age starts here, asleep too (AQ01, DA01)
    before = _run(['check', email], runner)[0]   # always the CURRENT entitlement, never a historical receipt (S14)
    if not (_names(before, 'ACTIVE', email) or _names(before, 'NONE', email)):   # failed or someone else's (R12, S13)
        journal.event(creator_key, 'grant-error', f'{email}:check', {'step': 'check', 'line': before})
        return False, before
    active = _names(before, 'ACTIVE', email)
    # the last instant before the grant OR the ownership record: everything re-checked, nothing claimed yet
    # (W03, X01; ACTIVE too, review Y02)
    guard, started = _guard(), checked_at   # check, guard and ownership all inside one window (AQ01)
    stop = guard() if guard else []
    if stop:
        journal.event(creator_key, 'grant-error', f'{email}:stopped', {'reasons': stop})
        return False, 'stopped before granting: ' + '; '.join(stop)
    fresh = (lambda: started.age() <= _span()) if guard else (lambda: True)
    settled = journal.settle_premium(creator_key, email, active, fresh)   # owners re-read and claimed atomically (X02)
    if settled == 'stale':   # waited too long for the write lock: the checks may be out of date, nothing claimed (Y01)
        journal.event(creator_key, 'grant-error', f'{email}:stale', {'step': 'settle'})
        return False, 'stopped before granting: the checks went stale while waiting; try again'
    if settled == 'ok' and not active and not fresh():   # the claim's commit itself stalled (AB02): never grant late.
        # The claim stays: the next attempt sees 'unresolved' and the captain checks by hand, never a blind retry.
        journal.event(creator_key, 'grant-error', f'{email}:stale-claim', {'step': 'settle-commit'})
        return False, 'stopped before granting: the checks went stale while recording the claim; check by hand'
    if settled == 'other':
        journal.event(creator_key, 'grant-error', f'{email}:owner', {'step': 'check', 'line': before})
        return False, 'this Premium account already belongs to another creator; the captain decides'
    if settled == 'other-email':
        journal.event(creator_key, 'grant-error', f'{email}:other-email', {'step': 'settle'})
        return False, 'she already has (or an attempt claimed) Premium on another email; a change is for the captain'
    if settled == 'revoked':
        journal.event(creator_key, 'grant-error', f'{email}:revoked', {'step': 'check', 'line': before})
        return False, 'Premium was granted before but is not active now (revoked or ended); the captain decides'
    if settled == 'unresolved':
        journal.event(creator_key, 'grant-error', f'{email}:unresolved', {'step': 'check', 'line': before})
        return False, 'an earlier grant attempt for this email never confirmed; check by hand'
    if active:
        line = f'GRANTED (already active per check): {before}'
    else:
        line = _run(['grant', email, '--note', note], runner)[0]
        if not _names(line, 'GRANTED', email):
            after = _run(['check', email], runner)[0]          # unclear: check, never grant twice
            journal.event(creator_key, 'grant-error', f'{email}:grant', {'step': 'grant', 'line': line, 'check': after})
            if not _names(after, 'ACTIVE', email):
                return False, line
            line = f'GRANTED (confirmed by check after an unclear result): {after}'
        journal.event(f'premium:{email}', 'premium-acknowledged', email, {'email': email, 'by': creator_key})
    journal.event(creator_key, 'premium-granted', email, {'email': email, 'result': line, 'note': note})
    return True, line
