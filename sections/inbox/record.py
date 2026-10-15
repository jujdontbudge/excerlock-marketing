"""One creator, everything in one place: messages on every channel (including the captain's own), every gate
decision, every state change, every captain decision, her SideShift contracts and her free-Premium status.

  .venv/bin/python sections/inbox/record.py show "Kamila Rueda"            # print it
  .venv/bin/python sections/inbox/record.py show "Kamila Rueda" --html out.html
  .venv/bin/python sections/inbox/record.py decide "Kamila Rueda" "ask for a brand new TikTok" --by captain
  .venv/bin/python sections/inbox/record.py keep-invite "Dakota McGaughy" "she is trying, keep her spot"
  .venv/bin/python sections/inbox/record.py answered "Kamila Rueda" <message id>   # the gate stops holding for it
  .venv/bin/python sections/inbox/record.py looked-at "Dakota McGaughy" <message id>  # an attachment was checked
  .venv/bin/python sections/inbox/record.py dnc "Name" on --why "asked us to stop"

Sources are read, never copied into a second store: the gate journal (decisions, events), contacts-mcp (messages),
SideShift (live chat, contracts) and excerlock-access (Premium). Captain decisions are appended to the journal.
"""
import argparse
import html
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / 'integrations/sideshift'))

from gate.journal import Journal  # noqa: E402

COMPANY = 'L9suC60QYBRzy8rRY16r1FtjyPT2'


def find_creator(client, name_or_id):
    hits = []
    for c in client.pages('/conversations'):
        for p in c.get('participants', []):
            if name_or_id in (p.get('name'), p.get('id')):
                hits.append((p['id'], p.get('name'), c['id']))
    if len(hits) != 1:
        sys.exit(f'{len(hits)} SideShift chats match {name_or_id!r}; refusing to guess')
    return hits[0]


def read_for_captain(live, chat_id, uid):
    """The chat for the captain to look at and settle. If it can't be read completely, show what WAS read (veto-only
    partial evidence) instead of failing, so unreadable messages can still be settled (review BI02). Automation never
    uses this: it always needs a complete read."""
    from gate.live import LiveReadError
    try:
        return live.read(chat_id, [uid])
    except LiveReadError as exc:
        if getattr(exc, 'partial', None) is None:
            raise
        print(f'note: the chat could not be read completely ({exc}); showing what was read')
        return exc.partial


def build(journal, live, contracts, uid, name, chat_id, premium_email=None):
    key = f'sideshift:{uid}'
    from gate import checks as _checks
    conv = _checks.with_history(read_for_captain(live, chat_id, uid), journal.events(key))   # vanished messages too (AY01)
    timeline = []
    for m in conv.messages:
        who = {'in': name, 'out': 'Johan' if m.author == 'captain' else 'ExcerLock (bot)'}.get(m.direction, 'UNKNOWN SENDER')
        timeline.append((m.at, f'msg {m.id[:8]}', f'{who}: {m.text}' + (f' [+{m.attachments} attachment]' if m.attachments else '')))
    for d in journal.history(key):
        timeline.append((d['at'], f"gate {d['outcome']}", f"{d['message_type']}: {d['reasons']}" + (f" → {d['text']!r}" if d['outcome'] == 'sent' else '')))
    for e in journal.events(key):
        timeline.append((e['at'], e['kind'], f"{e['ref'] or ''} {e['data']}"))
    timeline.sort(key=lambda t: t[0])
    premium = None
    if premium_email:
        premium = subprocess.run(['excerlock-access', 'check', premium_email], capture_output=True, text=True).stdout.strip()
    return {'name': name, 'key': key, 'chat': chat_id, 'contracts': contracts, 'premium': premium, 'timeline': timeline}


def as_text(r):
    lines = [f"# {r['name']}  ({r['key']}, SideShift chat {r['chat']})"]
    for c in r['contracts']:
        lines.append(f"Contract {c['id']}: {c.get('status')}  (created {c.get('createdAt')})")
    if r['premium']:
        lines.append(f"Premium: {r['premium']}")
    lines.append('')
    lines += [f'{at[:16]}  {kind:16} {text}' for at, kind, text in r['timeline']]
    return '\n'.join(lines)


def as_html(r):
    rows = ''.join(f'<tr><td>{html.escape(at[:16])}</td><td>{html.escape(kind)}</td><td>{html.escape(text)}</td></tr>'
                   for at, kind, text in r['timeline'])
    head = ''.join(f"<p>Contract {html.escape(c['id'])}: <b>{html.escape(str(c.get('status')))}</b></p>" for c in r['contracts'])
    return (f"<!doctype html><meta charset=utf-8><title>{html.escape(r['name'])}</title>"
            f"<style>body{{font:14px -apple-system,sans-serif;margin:24px}}td{{padding:4px 8px;vertical-align:top;border-bottom:1px solid #eee}}</style>"
            f"<h1>{html.escape(r['name'])}</h1>{head}<p>{html.escape(r['premium'] or '')}</p><table>{rows}</table>")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('show'); s.add_argument('creator'); s.add_argument('--html'); s.add_argument('--email')
    d = sub.add_parser('decide'); d.add_argument('creator'); d.add_argument('decision'); d.add_argument('--by', default='captain')
    k = sub.add_parser('keep-invite'); k.add_argument('creator'); k.add_argument('why')
    a = sub.add_parser('answered', help='mark her message(s) answered: the gate stops holding for them')
    a.add_argument('creator'); a.add_argument('message_id', nargs='+'); a.add_argument('--why', default='answered by the captain')
    lk = sub.add_parser('looked-at', help='mark an attachment as looked at')
    lk.add_argument('creator'); lk.add_argument('message_id', nargs='+')
    dn = sub.add_parser('dnc', help='do-not-contact on/off for this creator (every automatic message stops)')
    dn.add_argument('creator'); dn.add_argument('state', choices=('on', 'off')); dn.add_argument('--why', default='')
    args = ap.parse_args()
    from dotenv import load_dotenv
    load_dotenv(REPO / '.env')
    from client import Client
    from gate.live import SideShiftLive, collect_contracts
    journal = Journal()   # first: every read below journals signing evidence as it goes (review AK02)
    client = Client()
    uid, name, chat = find_creator(client, args.creator)
    key = f'sideshift:{uid}'
    contracts = [c for c in collect_contracts(Client(os.environ['SIDESHIFT_CONTRACTS_KEY']), 'v4mH50Sz9sUdkssqcd2L',
                                              journal.remember_contract) if c.get('contractorId') == uid]
    if args.cmd == 'decide':
        from datetime import datetime, timezone
        journal.event(key, 'captain-decision', datetime.now(timezone.utc).isoformat(), {'decision': args.decision, 'by': args.by})
        print(f'recorded for {name}: {args.decision}')
    elif args.cmd in ('answered', 'looked-at'):
        from gate import checks
        from gate.live import SideShiftLive
        kind = 'answered' if args.cmd == 'answered' else 'attachment-reviewed'
        conv = checks.with_history(read_for_captain(SideShiftLive(client, COMPANY, on_notice=journal.remember_notice), chat, uid),
                                   journal.events(key))   # vanished messages can be marked too (AY01)
        from gate.live import revision_key
        open_ones = list(conv.messages)   # deleted ones too: they can need a mark (review BD01, BE02)
        for mid in args.message_id:   # a message id OR a revision key; never guess between revisions (review BA03)
            exact = [x for x in open_ones if revision_key(x) == mid or x.id == mid]
            matches = exact or [x for x in open_ones if revision_key(x).startswith(mid)]
            if len(matches) != 1:
                print(f'{mid}: matches {len(matches)} message versions; pick one by its revision key:')
                for x in matches:
                    state = 'gone from the chat' if x.vanished else 'in the chat now'
                    print(f'  {revision_key(x)}  ({state}, {x.attachments} file(s)): {x.text[:60]!r}')
                continue
            m = matches[0]
            if kind == 'attachment-reviewed' and (m.attachments_sig or '').startswith('u-'):
                print(f'{mid}: this file has nothing that identifies it, so a look can\'t be recorded; '
                      f'automation stays held for {name}. Handle her messages by hand.')   # review BK01
                continue
            info = {'by': 'captain', 'why': getattr(args, 'why', ''), 'text': m.text[:120]}
            if kind == 'answered':   # edit-bound, and a fresh fact each time (BZ01, CA01)
                journal.answer(key, checks.answer_mark(m), info)
            else:
                journal.event(key, kind, checks.mark(m), info)
            print(f'{name}: marked {kind}: {m.text[:80]!r}')
    elif args.cmd == 'dnc':
        from datetime import datetime, timezone
        journal.event(key, 'do-not-contact', datetime.now(timezone.utc).isoformat(), {'enabled': args.state == 'on', 'why': args.why})
        if args.state == 'off':   # the captain's release also clears a remembered contacts tag (review CY01)
            journal.event(key, 'remote-dnc', datetime.now(timezone.utc).isoformat(), {'enabled': False, 'why': args.why})
        print(f'{name}: do-not-contact {args.state}')
    elif args.cmd == 'keep-invite':
        for c in contracts:
            journal.event(key, 'keep-invite', c['id'], {'why': args.why})
        print(f'{name}: invite kept ({len(contracts)} contract(s)); it will not be withdrawn automatically')
    else:
        r = build(journal, SideShiftLive(client, COMPANY, on_notice=journal.remember_notice), contracts, uid, name, chat, args.email)
        if args.html:
            Path(args.html).write_text(as_html(r))
            print(args.html)
        else:
            print(as_text(r))


if __name__ == '__main__':
    main()
