"""Required-behavior assertions: each fails on the reviewed code. No network.

python3 -m unittest discover -s out/tests -t .
"""
import sys
import types
from contextlib import ExitStack, redirect_stdout
from datetime import timedelta
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from gate.dispatch import Gate
from gate.live import SideShiftLive
from gate.tests.review4.support import Case, NOW, Live, conv, flow, invite, policy, withdraw
from gate.tests.review7.test_round7 import CheckedSender


class PartialApplicationReads(Case):
    def configured_gate(self, failed_read):
        """Capture flow.main's actual Gate and nested application reader, without running Flow.

        The initial Flow-wide read (fixed by AD01) is deliberately not the source of
        evidence here: a request appears in the later per-send read instead.
        """
        calls, yielded, captured = [], [], []
        application = dict(id='request1', programId=flow.CAMPAIGN, creator={'id': 'U1'},
                           status='pending', requestedAt=NOW.isoformat())
        source = Live(conv(invite()))
        sender = CheckedSender(source)

        class Client:
            def __init__(inner, *args):
                pass

            def pages(inner, path, **kwargs):
                self.assertEqual(path, '/applications')
                calls.append(path)
                if len(calls) == failed_read:
                    yielded.append(application)
                    yield application
                    raise OSError('next application page unavailable')

            def request(inner, method, path):
                return {'data': self.contract()}

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
        gate = captured[0]
        result = gate.run(self.action(message_type='contract-reminder-1', fields={'First': 'Ada'}))
        self.assertEqual(yielded, [application], 'The real per-send reader must consume the positive row')
        self.assertEqual(result.outcome, 'held', result.reasons)
        self.assertEqual(sender.delivered, [], 'Incomplete coverage must hold the first attempt')
        return gate, sender

    def test_AE01_partial_initial_gate_applications_survive_before_later_reminder(self):
        gate, sender = self.configured_gate(failed_read=1)
        # Request is redacted; six hours later a complete empty read cannot undo it.
        gate.now = lambda: NOW + timedelta(hours=6)
        result = gate.run(self.action(message_type='contract-reminder-2', fields={'First': 'Ada'}))
        self.assertEqual(sender.delivered, [],
                         f'Gate consumed signing six hours earlier, but reminder {result.outcome}')

    def test_AE01_partial_fresh_contract_applications_survive_before_later_withdrawal(self):
        self.configured_gate(failed_read=2)  # first read empty; post-review read sees the request then fails
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        result = withdraw.withdraw('C1', lambda cid: self.contract(), lambda: conv(invite()),
                                   self.j, 'sideshift:U1', NOW + timedelta(hours=30), writer, lambda: [])
        self.assertEqual(writes, [],
                         f'Gate consumed signing 30 hours earlier, but withdrawal {result}')


class PartialChatReads(Case):
    def failed_chat_read(self, normalization=False):
        rows = [
            dict(id='invite1', createdAt=(NOW - timedelta(hours=10)).isoformat(),
                 senderUserId=flow.COMPANY, content='https://app.sideshift.app/campaign-invite/C1'),
            dict(id='request1', createdAt=NOW.isoformat(), senderUserId='U1',
                 content='📨 Requested 2 handles for this contract.'),
        ]
        if normalization:
            rows.append(dict(id='bad-row', senderUserId='U1', content='Malformed timestamp'))
        phase, yielded = ['failed'], []

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    yield {'id': 'chat1', 'members': [flow.COMPANY, 'U1']}
                    return
                self.assertEqual(path, '/support-channels/chat1/messages')
                for row in rows if phase[0] == 'failed' else rows[:1]:
                    yielded.append(row['id'])
                    yield row
                if phase[0] == 'failed' and not normalization:
                    raise OSError('next chat page unavailable')

        source = SideShiftLive(Client(), flow.COMPANY)
        sender = CheckedSender(source)
        gate = self.gate(types=policy.load(), source=source, sender=sender,
                         reader=lambda cid: self.contract())
        gate.applications_reader = lambda uid: []
        result = gate.run(self.action(message_type='contract-reminder-1', fields={'First': 'Ada'}))
        self.assertIn('request1', yielded, 'The real live reader must consume the signing notice')
        self.assertEqual(result.outcome, 'held', result.reasons)
        self.assertIn('no complete live read', result.reasons[0])
        self.assertEqual(sender.delivered, [])
        phase[0] = 'redacted'
        return gate, sender

    def test_AE02_partial_chat_page_survives_before_later_reminder(self):
        gate, sender = self.failed_chat_read()
        gate.now = lambda: NOW + timedelta(hours=6)
        result = gate.run(self.action(message_type='contract-reminder-2', fields={'First': 'Ada'}))
        self.assertEqual(sender.delivered, [],
                         f'Live reader consumed signing six hours earlier, but reminder {result.outcome}')

    def test_AE02_later_malformed_chat_row_preserves_signing_before_withdrawal(self):
        gate, sender = self.failed_chat_read(normalization=True)
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        result = withdraw.withdraw('C1', lambda cid: self.contract(),
                                   lambda: gate.live.read('chat1', ['U1']), self.j,
                                   'sideshift:U1', NOW + timedelta(hours=30), writer, lambda: [])
        self.assertEqual(writes, [],
                         f'Positive notice normalized before a bad row 30 hours earlier; withdrawal {result}')
