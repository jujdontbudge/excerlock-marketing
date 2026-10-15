"""One-time: record sends made before the gate existed (2026-10-14), so the gate never repeats them.

- Old reminders (~/Library/Logs/excerlock-inbox/reminders.json): a row without an error was seen delivered in the
  live chats on 2026-10-15 (Claude read all six chats) and is recorded 'sent'; a row with an error, a skip or an
  unreadable number is 'uncertain' (spent, never resent, shown to the captain) or skipped with a warning (G23).
- The captain-ordered "send me your email" messages to Jillian Collins and P Hudson, pinned to their SideShift
  user ids, never names.
Keys use the gate's format (gate.dispatch.Gate.key), including the invite round when `generations` is given.
Safe to run again: it never records a key twice.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate.dispatch import Gate  # noqa: E402
from gate.journal import Journal  # noqa: E402
from gate.model import Action, Decision  # noqa: E402
from gate.policy import load  # noqa: E402

OLD = Path.home() / 'Library/Logs/excerlock-inbox/reminders.json'
PRE_GATE_EMAIL_ASKS = {'rzFGIws4gUaiXfouNutBRMHrdgm2': 'Jillian Collins', 'VMpXInwUCLQfdCsIWyvkgM7fMJv2': 'P Hudson'}


def seed(journal, contracts, generations=None, types=None):
    generations = generations or {}
    types = types or load()
    keyer = Gate(types, None, None, None, journal)
    by_id = {c['id']: c for c in contracts}
    done, warnings = [], []
    state = json.loads(OLD.read_text()) if OLD.exists() else {}
    for cid, st in state.items():
        if cid.startswith('_') or cid not in by_id or not isinstance(st, dict):
            continue
        contract = {**by_id[cid], 'inviteGeneration': generations.get(cid)}
        rows = st.get('reminders')
        if not isinstance(rows, list):
            if rows is not None:
                warnings.append(f'{cid}: reminders is not a list, skipped')
            continue
        for r in rows:
            try:
                n = int(r['n'])
                kinds = [f'contract-reminder-{n + 1}']
                if kinds[0] not in types:
                    raise ValueError(kinds[0])
                proven = not r.get('error') and not r.get('skipped')
                reason = ('pre-gate send, seen in the live chat 2026-10-15' if proven
                          else f"pre-gate attempt, delivery not proven ({r.get('error') or r.get('skipped')})")
            except (KeyError, TypeError, ValueError, AttributeError):
                # unreadable: we can't tell which reminder it was, so block both (review N21), never allow a repeat
                kinds = [k for k in ('contract-reminder-1', 'contract-reminder-2') if k in types]
                proven, reason = False, f'unreadable legacy row {r!r}: delivery unknown'
                warnings.append(f'{cid}: unreadable legacy row {r!r}, both reminders blocked')
            for mt in kinds:
                a = Action(message_type=mt, channel='sideshift', conversation_id='pre-gate', source_chat_id='', person_id=None,
                           creator_key=f"sideshift:{contract['contractorId']}", occurrence=cid, contract=contract,
                           trigger='sent by the old contract_reminders.py before the gate existed')
                key = keyer.key(types[mt], a)
                if journal.spent(key):
                    continue
                journal.record(a, key, Decision('sent' if proven else 'uncertain', [reason], '(old reminder text)'))
                done.append(key)
    for c in contracts:
        if c.get('contractorId') not in PRE_GATE_EMAIL_ASKS:   # pinned by stable id; names can change (review N21)
            continue
        ck = f"sideshift:{c['contractorId']}"
        a = Action(message_type='ask-app-email', channel='sideshift', conversation_id='pre-gate', source_chat_id='',
                   person_id=None, creator_key=ck, trigger='captain order 2026-10-14 "yes do that"')
        key = keyer.key(types['ask-app-email'], a)
        if not journal.spent(key):
            journal.record(a, key, Decision('sent', ['pre-gate captain-ordered send, seen in the live chat 2026-10-15'],
                                            '(asked for her app email)'))
            done.append(key)
    return done, warnings


if __name__ == '__main__':
    import os
    REPO = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(REPO / 'integrations/sideshift'))
    from dotenv import load_dotenv
    load_dotenv(REPO / '.env')
    from client import Client
    from gate import checks
    from gate.live import SideShiftLive, collect_contracts
    journal = Journal()   # first: contract and chat reads journal signing evidence as they go (review AK02)
    contracts = collect_contracts(Client(os.environ['SIDESHIFT_CONTRACTS_KEY']), 'v4mH50Sz9sUdkssqcd2L', journal.remember_contract)
    live = SideShiftLive(Client(), 'L9suC60QYBRzy8rRY16r1FtjyPT2', on_notice=journal.remember_notice)
    chats = {}
    for conv in live.client.pages('/conversations'):
        for m in conv.get('members', []):
            chats.setdefault(m, []).append(conv['id'])
    generations = {}
    for c in contracts:
        found = chats.get(c['contractorId'], [])
        if len(found) == 1:
            generations[c['id']] = checks.invite_generation(live.read(found[0], [c['contractorId']]), c)
    done, warnings = seed(journal, contracts, generations)
    for k in done:
        print('seeded', k)
    for w in warnings:
        print('WARNING', w)
