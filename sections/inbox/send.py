"""Send one message to a SideShift creator THROUGH THE GATE, on the captain's explicit order.

  .venv/bin/python sections/inbox/send.py --creator "Kamila Rueda" --type ask-app-email --order "yes do that"
  .venv/bin/python sections/inbox/send.py --creator "P Hudson" --text "exact words" --order "<his words>" --occurrence p-new-accounts
  add --contract <id> when she has more than one contract; add --dry-run to see the decision without sending.

This command is the captain's interface: it records a one-use approval bound to her, the message type, the occurrence
and the exact text, and only that approval lets the gate skip quiet hours, the minimum gap, draft mode and PAUSED.
Everything else still applies: live read, lock, binding, unknown senders, already-sent and the full-chat review.
Dry runs use a throwaway copy of the real journal, so they see what was really sent and leave nothing behind.
"""
import argparse
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / 'integrations/sideshift'))

from gate import policy  # noqa: E402
from gate.dispatch import CAPTAIN_TEXT, Gate, text_hash  # noqa: E402
from gate.journal import Journal, snapshot  # noqa: E402
from gate.live import SideShiftLive, collect_applications, collect_contracts  # noqa: E402
from gate.model import Action  # noqa: E402

COMPANY = 'L9suC60QYBRzy8rRY16r1FtjyPT2'
CAMPAIGN = 'v4mH50Sz9sUdkssqcd2L'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--creator', required=True, help='her SideShift display name or user id')
    ap.add_argument('--type', help='an approved message type in sections/inbox/messages/')
    ap.add_argument('--text', help="the captain's exact words (instead of --type)")
    ap.add_argument('--order', required=True, help="the captain's words ordering this send")
    ap.add_argument('--occurrence', default='', help='makes the send unique (required with --text)')
    ap.add_argument('--contract', default='', help='which contract, when she has more than one')
    ap.add_argument('--field', action='append', default=[], help='name=value for template fields')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    if bool(args.type) == bool(args.text):
        sys.exit('give exactly one of --type or --text')
    if args.text and not args.occurrence:
        sys.exit('--text needs --occurrence (a short unique name for this message)')
    from dotenv import load_dotenv
    load_dotenv(HERE.parents[1] / '.env')
    from client import Client
    from flow import contacts_routes
    from gate.contacts import ContactsMCP
    from gate.review import ClaudeReviewer

    if args.dry_run:
        journal = snapshot(Path(tempfile.mkdtemp(prefix='gate-dry-')) / 'gate.db')
    else:
        journal = Journal()
    # every chat read journals signing notices as it goes, from the very first read (review AJ01)
    live = SideShiftLive(Client(), COMPANY, on_notice=journal.remember_notice)
    hits = [(c, p) for c in live.client.pages('/conversations') for p in c.get('participants', [])
            if p.get('id') != COMPANY and args.creator in (p.get('name'), p.get('id'))]
    if len(hits) != 1:
        sys.exit(f'{len(hits)} SideShift chats match {args.creator!r}; refusing to guess')
    chat, person = hits[0]
    uid, first = person['id'], (person.get('name') or '').split(' ')[0]
    contracts_client = Client(os.environ['SIDESHIFT_CONTRACTS_KEY'])
    contracts = [c for c in collect_contracts(contracts_client, CAMPAIGN, journal.remember_contract)   # AJ02
                 if c.get('contractorId') == uid]
    if args.contract:
        contracts = [c for c in contracts if c.get('id') == args.contract]
        if not contracts:
            sys.exit(f'no contract {args.contract} for {args.creator}')
    if len(contracts) > 1:
        sys.exit(f'{len(contracts)} contracts for {args.creator}; pick one with --contract ({", ".join(c["id"] for c in contracts)})')
    contract = contracts[0] if contracts else None

    def read_contract(contract_id):
        got = contracts_client.request('GET', f'/contracts/{contract_id}')
        return got.get('data', got) if isinstance(got, dict) else got

    contacts = ContactsMCP()
    contacts.live = live   # the sender re-reads the chat right before sending (review N01)
    conversation_id, person_id = contacts_routes(contacts)(chat['id'])
    fields = dict(f.split('=', 1) for f in args.field)
    fields.setdefault('First', first)
    fields.setdefault('first', first.lower())
    if args.text:
        fields['text'] = args.text
    message_type = CAPTAIN_TEXT if args.text else args.type
    if contract:
        from gate import checks
        contract = {**contract, 'recorded_invites': checks.recorded_invites(contract, journal.events(f'sideshift:{uid}'))}
        # the same round the gate will compute: the live chat plus invites journaled earlier (review AU02)
        contract = {**contract, 'inviteGeneration': checks.invite_generation(live.read(chat['id'], [uid]), contract)}
    occurrence = args.occurrence or (contract['id'] if contract else '')
    types = policy.load()
    t = types.get(message_type)
    try:
        text = args.text.strip() if args.text else policy.render(t, fields)
    except (AttributeError, policy.PolicyError) as exc:
        sys.exit(f'cannot render {message_type}: {exc}')
    approval = journal.approve(f'sideshift:{uid}', message_type, occurrence, text_hash(text), args.order)

    class Dry:
        def preflight(self, action):
            if hasattr(contacts, 'preflight'):
                contacts.preflight(action)

        def send(self, action, text, key, auth):
            print(f'DRY RUN, would send: {text!r}')
            return {'status': 'sent', 'id': 'dry-run'}
    import grant

    def granter(action):   # live entitlement check (and grant if needed) before any "Premium is on" message (S14)
        if args.dry_run:
            return True, 'DRY RUN: would check/grant'
        return grant.grant(journal, action.creator_key, action.fields['email'], f'UGC {first}, captain order: {args.order}'[:200])
    read_key = os.environ.get('SIDESHIFT_READ_KEY')
    read_client = Client(read_key) if read_key else None

    def read_applications(uid):
        if read_client is None:
            raise RuntimeError('no SIDESHIFT_READ_KEY')
        return collect_applications(read_client, CAMPAIGN, uid,   # rows journaled as read; kept on a failed page (AE01, AH02)
                                    on_row=lambda owner, a: journal.remember_request(f'sideshift:{owner}', a))
    gate = Gate(types, live, ClaudeReviewer(), Dry() if args.dry_run else contacts, journal, contract_reader=read_contract,
                granter=granter, applications_reader=read_applications,
                entitlement=(lambda e: True) if args.dry_run else grant.active)
    d = gate.run(Action(message_type=message_type, channel='sideshift', conversation_id=conversation_id or 'unrouted',
                        source_chat_id=chat['id'], person_id=person_id, creator_key=f'sideshift:{uid}', fields=fields,
                        trigger='captain order', occurrence=occurrence, captain_order=args.order, approval_id=approval,
                        contract=contract))
    print(f'{d.outcome.upper()}: {"; ".join(d.reasons)}')
    if d.text:
        print(f'text: {d.text!r}')


if __name__ == '__main__':
    main()
