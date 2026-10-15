"""Required safety assertions, intentionally failing on the reviewed source. No network.

Run: python3 -m unittest discover -s out/tests -t .
Real Gate, SideShiftLive, application collector, Flow, ContactsMCP boundary and SQLite.
Only service responses, time and the full-chat review verdict are faked.
"""
import sys
import types
from contextlib import ExitStack, redirect_stdout
from dataclasses import replace
from datetime import timedelta
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from gate import checks
from gate.dispatch import Gate
from gate.live import SideShiftLive
from gate.tests.review4.support import Case, NOW, Live, conv, flow, invite, policy, withdraw
from gate.tests.review7.test_round7 import CheckedSender


class ReviewCase(Case):
    def configured(self, source, contract=None):
        contract = contract or self.contract()
        sender = CheckedSender(source)
        gate = self.gate(types=policy.load(), source=source, sender=sender,
                         reader=lambda cid: dict(contract))
        gate.applications_reader = lambda uid: []
        return gate, sender

    def production_gate(self, source, application_client, contract):
        """Capture flow.main's real per-send reader and Gate wiring, without running a job."""
        captured = []
        sender = CheckedSender(source)

        class Client:
            def __new__(cls, key=None):
                if key == 'offline-read':
                    return application_client
                return SimpleNamespace(request=lambda *a, **kw: {'data': dict(contract)})

        def make_gate(*args, **kwargs):
            gate = Gate(*args, **{**kwargs, 'now': lambda: NOW, 'paused_file': self.paused})
            captured.append(gate)
            return gate

        client, dotenv = types.ModuleType('client'), types.ModuleType('dotenv')
        client.Client, dotenv.load_dotenv = Client, lambda *args: None
        with ExitStack() as stack:
            stack.enter_context(patch.dict(sys.modules, {'client': client, 'dotenv': dotenv}))
            stack.enter_context(patch.dict('os.environ', {'SIDESHIFT_CONTRACTS_KEY': 'offline',
                                                        'SIDESHIFT_READ_KEY': 'offline-read',
                                                        'SIDESHIFT_CONTRACTS_WRITE_KEY': ''}))
            stack.enter_context(patch.object(sys, 'argv', ['flow.py']))
            stack.enter_context(patch.object(flow, 'Journal', return_value=self.j))
            stack.enter_context(patch.object(flow, 'SideShiftLive', return_value=source))
            stack.enter_context(patch.object(flow, 'Gate', side_effect=make_gate))
            stack.enter_context(patch.object(flow, 'Flow', return_value=SimpleNamespace(run=lambda: [])))
            stack.enter_context(patch.object(flow, 'contacts_routes', return_value=lambda chat: ('route1', 'person1')))
            stack.enter_context(patch('gate.contacts.ContactsMCP', return_value=sender))
            stack.enter_context(patch('gate.review.ClaudeReviewer', return_value=lambda *a: ('SEND', 'offline review', [])))
            stack.enter_context(redirect_stdout(StringIO()))
            flow.main()
        self.assertEqual(len(captured), 1)
        return captured[0], sender

    def reminder(self, gate, contract=None):
        return gate.run(self.action(message_type='contract-reminder-2', fields={'First': 'Ada'},
                                    contract=contract or self.contract()))

    def writer(self, writes):
        def request(*args, **kwargs):
            writes.append((args, kwargs))
            return {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'}
        return SimpleNamespace(request=request)


class DeletedFirstInvite(ReviewCase):
    def source(self):
        rows = [
            dict(id='first', createdAt=(NOW - timedelta(hours=30)).isoformat(),
                 senderUserId=flow.COMPANY,
                 content='https://app.sideshift.app/campaign-invite/C1', isDeleted=True),
            dict(id='request', createdAt=(NOW - timedelta(hours=28)).isoformat(),
                 senderUserId='U1', content='📨 Requested 2 handles for this contract.'),
            dict(id='reinvite', createdAt=(NOW - timedelta(hours=13)).isoformat(),
                 senderUserId=flow.COMPANY,
                 content='https://app.sideshift.app/campaign-invite/C1'),
        ]

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    return [{'id': 'chat1', 'members': [flow.COMPANY, 'U1']}]
                self.assertEqual(path, '/support-channels/chat1/messages')
                return rows

        source = SideShiftLive(Client(), flow.COMPANY)
        history = source.read('chat1', ['U1'])
        self.assertTrue(history.complete, 'No incomplete history or failed pagination in this case')
        self.assertEqual(len(history.messages), 3)
        # The same complete history with the original invite undeleted proves signing.
        rows[0]['isDeleted'] = False
        self.assertTrue(checks.signing_seen(source.read('chat1', ['U1']), self.contract()))
        rows[0]['isDeleted'] = True
        return source

    def test_AH01_deleted_first_invite_cannot_enable_a_reminder(self):
        source = self.source()
        gate, sender = self.configured(source)
        result = self.reminder(gate)
        self.assertEqual(sender.delivered, [],
                         f'Complete history contains her request after the original invite; {result.outcome}: {result.reasons}')

    def test_AH01_deleted_first_invite_cannot_erase_flow_evidence_before_withdrawal(self):
        source = self.source()
        draft_types = {k: replace(t, mode='draft')
                       for k, t in policy.load().items()}
        gate, sender = self.configured(source)
        gate.types = draft_types
        job = flow.Flow(SimpleNamespace(pages=lambda *a, **kw: [self.contract()]), source,
                        gate, self.j, lambda cid: ('route1', 'person1'), now=lambda: NOW,
                        read_client=SimpleNamespace(pages=lambda *a, **kw: []))
        job.run()
        self.assertEqual(sender.delivered, [])
        writes = []
        # Notice is redacted after the observation; both invite rows remain.
        later = Live(conv(invite(id='first', at=NOW - timedelta(hours=30), deleted=True),
                          invite(id='reinvite', at=NOW - timedelta(hours=13))))
        result = withdraw.withdraw('C1', lambda cid: self.contract(),
                                   lambda: later.read('chat1', ['U1']), self.j, 'sideshift:U1',
                                   NOW + timedelta(hours=24), self.writer(writes), lambda: [])
        self.assertEqual(writes, [], f'Flow read signing 24 hours earlier, but withdrawal {result}')


class PerSendPagination(ReviewCase):
    def application(self):
        return dict(id='request1', programId=flow.CAMPAIGN, creator={'id': 'U1'},
                    status='pending', requestedAt=(NOW - timedelta(hours=2)).isoformat())

    def test_AH02_consumed_request_must_stop_concurrent_flow_withdrawal_during_next_page(self):
        clock, consumed, writes, reports = [1000.0], [], [], []
        contract = self.contract(createdAt=(NOW - timedelta(hours=40)).isoformat())
        history = conv(invite(at=NOW - timedelta(hours=35, minutes=59)))

        class Source(Live):
            client = SimpleNamespace(pages=lambda *a, **kw: [
                {'id': 'chat1', 'members': [flow.COMPANY, 'U1']}])

        source = Source(history)
        def pages(path):
            self.assertEqual(path, '/applications')
            consumed.append('request1')
            yield self.application()
            # The real collector has appended the row and now asks for another page.
            # During 120s of page I/O, the service redacts the request. Another job
            # sees complete empty requests, and this invite has crossed 36 hours.
            clock[0] += 120.0
            contracts = SimpleNamespace(pages=lambda *a, **kw: [dict(contract)],
                                        request=lambda *a, **kw: {'data': dict(contract)})
            job = flow.Flow(contracts, source, None, self.j, lambda cid: ('route1', 'person1'),
                            now=gate.now, write_client=self.writer(writes),
                            read_client=SimpleNamespace(pages=lambda *a, **kw: []))
            reports.extend(job.run())

        gate, sender = self.production_gate(source, SimpleNamespace(pages=pages), contract)
        gate.now = lambda: NOW + timedelta(seconds=clock[0] - 1000.0)
        with patch('time.monotonic', side_effect=lambda: clock[0]):
            result = self.reminder(gate, dict(contract))
        self.assertEqual(consumed, ['request1'])
        self.assertEqual(result.outcome, 'held', result.reasons)
        self.assertEqual(sender.delivered, [])
        self.assertEqual(writes, [],
                         f'Consumed signing remained only in the collector during page I/O: {reports}')

    def test_AH02_interrupted_next_page_cannot_erase_consumed_request_before_later_reminder(self):
        source = Live(conv(invite(at=NOW - timedelta(hours=10))))
        clock, consumed = [1000.0], []

        def pages(path):
            self.assertEqual(path, '/applications')
            consumed.append('request1')
            yield self.application()
            clock[0] += 120.0
            raise KeyboardInterrupt('worker stopped during slow page 2')

        gate, sender = self.production_gate(source, SimpleNamespace(pages=pages), self.contract())
        with patch('time.monotonic', side_effect=lambda: clock[0]):
            with self.assertRaises(KeyboardInterrupt):
                self.reminder(gate)
        self.assertEqual(consumed, ['request1'])
        self.assertEqual(clock[0], 1120.0, 'Not the accepted split-second crash/write gap')
        self.assertEqual(sender.delivered, [])
        # A restarted worker, six hours later, sees a complete but now empty list.
        later, sender = self.configured(source)
        later.now = lambda: NOW + timedelta(hours=6)
        result = self.reminder(later)
        self.assertEqual(sender.delivered, [],
                         f'Positive row consumed six hours earlier was never journaled; {result.outcome}: {result.reasons}')
