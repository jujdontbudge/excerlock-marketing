"""Safety assertions that fail on the reviewed source. Offline, no real sends.

Run: python3 -m unittest discover -s out/tests -t .
Real Gate, SideShiftLive, Flow, production flow.main application reader, ContactsMCP
send/preflight and file-backed SQLite. Service responses and clock are fakes.
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from gate.live import SideShiftLive
from gate.tests.review20 import test_round20 as previous
from gate.tests.review4.support import NOW, flow, policy
from gate.tests.review7.test_round7 import CheckedSender


def raw_invite(uid='U1', hours=10):
    return dict(id=f'invite-{uid}', createdAt=(NOW - timedelta(hours=hours)).isoformat(),
                senderUserId=flow.COMPANY,
                content=f'https://app.sideshift.app/campaign-invite/C{uid[1:]}')


def raw_request():
    return dict(id='notice1', createdAt=(NOW - timedelta(hours=2)).isoformat(),
                senderUserId='U1', content='📨 Requested 2 handles for this contract.')


def clean_source(invites):
    class Client:
        def pages(self, path, **kwargs):
            if path == '/conversations':
                return [dict(id=f'chat{uid[1:]}', members=[flow.COMPANY, uid]) for uid in invites]
            uid = 'U' + path.split('/')[2][4:]
            return [invites[uid]]
    return SideShiftLive(Client(), flow.COMPANY)


class MultiSender(CheckedSender):
    def call(self, tool, args):
        if tool == 'get_conversation':
            n = args['conversation_id'].removeprefix('route')
            return dict(id=args['conversation_id'], channel='sideshift', external_id=f'sideshift:chat{n}',
                        participants=[dict(value_normalized=f'U{n}', person_id=f'person{n}')])
        return super().call(tool, args)


class ReviewCase(previous.ReviewCase):
    def setUp(self):
        super().setUp()
        self.db = self.root / 'shared.db'
        self.j = self.new_journal(self.db)

    def contract_for(self, n=1):
        return self.contract(id=f'C{n}', contractorId=f'U{n}',
                             createdAt=(NOW - timedelta(hours=40)).isoformat())

    def concurrent_withdrawal(self, source, n, now, writes):
        contract = self.contract_for(n)
        contracts = SimpleNamespace(pages=lambda *a, **kw: [dict(contract)],
                                    request=lambda *a, **kw: {'data': dict(contract)})
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 dict(id=f'C{n}', contractorId=f'U{n}', status='rejected'))
        other_journal = self.new_journal(self.db)
        job = flow.Flow(contracts, source, None, other_journal,
                        lambda chat: (f'route{n}', f'person{n}'), now=now,
                        write_client=writer,
                        read_client=SimpleNamespace(pages=lambda *a, **kw: []))
        return job.run()

    def later_reminder(self, source, n=1):
        sender = MultiSender(source)
        # A new connection models a restarted worker; current application reads are complete/empty.
        gate = self.gate(types=policy.load(), source=source, sender=sender,
                         reader=lambda cid: self.contract_for(n))
        gate.journal = self.new_journal(self.db)
        gate.applications_reader = lambda uid: []
        gate.now = lambda: NOW + timedelta(hours=6)
        result = gate.run(self.action(message_type='contract-reminder-2', fields={'First': 'Ada'},
                                      creator_key=f'sideshift:U{n}', conversation_id=f'route{n}',
                                      source_chat_id=f'chat{n}', person_id=f'person{n}',
                                      contract=self.contract_for(n), occurrence=f'C{n}'))
        self.assertEqual(sender.delivered, [],
                         f'Signing consumed six hours earlier was forgotten: {result.outcome}: {result.reasons}')


class ChatPagination(ReviewCase):
    def test_AI01_interrupted_chat_pagination_cannot_erase_signing_before_later_reminder(self):
        clock, consumed, phase = [1000.0], [], ['reading']

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    yield dict(id='chat1', members=[flow.COMPANY, 'U1'])
                    return
                self.assertEqual(path, '/support-channels/chat1/messages')
                yield raw_invite()
                if phase[0] == 'reading':
                    consumed.append('notice1')
                    yield raw_request()
                    # The real live reader consumed the notice, then waits on page 2.
                    clock[0] += 120.0
                    raise KeyboardInterrupt('worker stopped during page 2')

        source = SideShiftLive(Client(), flow.COMPANY)
        gate, sender = self.configured(source, self.contract_for())
        with patch('time.monotonic', side_effect=lambda: clock[0]):
            with self.assertRaises(KeyboardInterrupt):
                self.reminder(gate, self.contract_for())
        self.assertEqual(consumed, ['notice1'])
        self.assertEqual(clock[0], 1120.0)
        self.assertEqual(sender.delivered, [])
        phase[0] = 'redacted'
        self.later_reminder(source)

    def test_AI01_consumed_chat_notice_must_stop_concurrent_flow_withdrawal_during_page_wait(self):
        clock, consumed, writes, reports = [1000.0], [], [], []
        row = raw_invite(hours=35 + 59 / 60)
        redacted = clean_source({'U1': row})
        now = lambda: NOW + timedelta(seconds=clock[0] - 1000.0)

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    yield dict(id='chat1', members=[flow.COMPANY, 'U1'])
                    return
                self.assertEqual(path, '/support-channels/chat1/messages')
                yield row
                consumed.append('notice1')
                yield raw_request()
                clock[0] += 120.0
                # Notice was redacted at SideShift during the wait; another real Flow
                # sees complete empty applications and a now-36-hour-old invitation.
                reports.extend(self.concurrent_withdrawal(redacted, 1, now, writes))

        source = SideShiftLive(Client(), flow.COMPANY)
        gate, sender = self.configured(source, self.contract_for())
        gate.now = now
        with patch('time.monotonic', side_effect=lambda: clock[0]):
            result = self.reminder(gate, self.contract_for())
        self.assertEqual(consumed, ['notice1'])
        self.assertEqual(result.outcome, 'held', result.reasons)
        self.assertEqual(sender.delivered, [])
        self.assertEqual(writes, [], f'Consumed notice was not durable during pagination: {reports}')


class OtherCreatorApplications(ReviewCase):
    def application(self):
        return dict(id='request-U2', programId=flow.CAMPAIGN, creator={'id': 'U2'},
                    status='pending', requestedAt=(NOW - timedelta(hours=2)).isoformat())

    def test_AI02_other_creators_consumed_request_survives_interruption_until_later_reminder(self):
        source = clean_source({'U1': raw_invite(), 'U2': raw_invite('U2')})
        clock, consumed = [1000.0], []

        def pages(path):
            self.assertEqual(path, '/applications')
            consumed.append('request-U2')
            yield self.application()
            clock[0] += 120.0
            raise KeyboardInterrupt('worker stopped during next application page')

        # Capture production wiring, then execute a real Gate for U1. The API is
        # campaign-wide, so its collector consumes U2's request along the way.
        gate, sender = self.production_gate(source, SimpleNamespace(pages=pages), self.contract_for())
        with patch('time.monotonic', side_effect=lambda: clock[0]):
            with self.assertRaises(KeyboardInterrupt):
                self.reminder(gate, self.contract_for())
        self.assertEqual(consumed, ['request-U2'])
        self.assertEqual(clock[0], 1120.0)
        self.assertEqual(sender.delivered, [])
        self.later_reminder(source, n=2)

    def test_AI02_other_creators_request_must_stop_concurrent_flow_withdrawal_in_draft_mode(self):
        clock, consumed, writes, reports = [1000.0], [], [], []
        source = clean_source({'U1': raw_invite()})
        other_source = clean_source({'U2': raw_invite('U2', hours=35 + 59 / 60)})
        now = lambda: NOW + timedelta(seconds=clock[0] - 1000.0)

        def pages(path):
            self.assertEqual(path, '/applications')
            consumed.append('request-U2')
            yield self.application()
            clock[0] += 120.0
            reports.extend(self.concurrent_withdrawal(other_source, 2, now, writes))

        gate, sender = self.production_gate(source, SimpleNamespace(pages=pages), self.contract_for())
        gate.types = {k: replace(t, mode='draft') for k, t in gate.types.items()}
        gate.now = now
        with patch('time.monotonic', side_effect=lambda: clock[0]):
            result = self.reminder(gate, self.contract_for())
        self.assertEqual(consumed, ['request-U2'])
        # adapted 2026-10-15 (review AJ03): reminder 2 at invite age 10h is now held by the gate's 12h schedule
        self.assertIn(result.outcome, ('draft', 'held'), result.reasons)
        self.assertEqual(sender.delivered, [])
        self.assertEqual(writes, [], f'Another creator was dropped by the production collector: {reports}')
