"""Safety assertions: intentionally fail on the reviewed source. Entirely offline.

Run: python3 -m unittest discover -s out/tests -t .
Real SideShiftLive, Flow, Gate, ContactsMCP send/preflight and SQLite journal;
only remote responses and the full-chat review verdict are faked.
"""
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.live import SideShiftLive
from gate.tests.review4.support import Case, NOW, flow, policy, withdraw
from gate.tests.review7.test_round7 import CheckedSender


def invite_row(cid='C1', id=None, hours=10):
    return dict(id=id or f'invite-{cid}', createdAt=(NOW - timedelta(hours=hours)).isoformat(),
                senderUserId=flow.COMPANY,
                content=f'https://app.sideshift.app/campaign-invite/{cid}')


def request_row():
    return dict(id='request1', createdAt=(NOW - timedelta(hours=8)).isoformat(),
                senderUserId='U1', content='📨 Requested 2 handles for this contract.')


class PersistenceCase(Case):
    def gate_for(self, source):
        sender = CheckedSender(source)
        gate = self.gate(types=policy.load(), source=source, sender=sender,
                         reader=lambda cid: self.contract())
        gate.applications_reader = lambda uid: []
        return gate, sender

    def later_reminder(self, source):
        gate, sender = self.gate_for(source)
        gate.now = lambda: NOW + timedelta(hours=6)
        result = gate.run(self.action(message_type='contract-reminder-2', fields={'First': 'Ada'}))
        self.assertEqual(sender.delivered, [],
                         f'Consumed signing was forgotten six hours later: {result.outcome}: {result.reasons}')

    def later_withdrawal(self, source):
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        result = withdraw.withdraw('C1', lambda cid: self.contract(),
                                   lambda: source.read('chat1', ['U1']), self.j,
                                   'sideshift:U1', NOW + timedelta(hours=30), writer, lambda: [])
        self.assertEqual(writes, [],
                         f'Consumed signing was forgotten 30 hours later: {result}')


class MissingFirstInvite(PersistenceCase):
    def partial_source(self):
        phase, consumed = ['complete'], []
        # Service order is newest first. The actual first invite is on an older page.
        rows = [invite_row(id='reinvite', hours=7), request_row(), invite_row()]

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    yield {'id': 'chat1', 'members': [flow.COMPANY, 'U1']}
                    return
                self.assertEqual(path, '/support-channels/chat1/messages')
                chosen = rows if phase[0] == 'complete' else rows[:2] if phase[0] == 'failed' else [rows[0], rows[2]]
                for row in chosen:
                    consumed.append(row['id'])
                    yield row
                if phase[0] == 'failed':
                    raise OSError('older page containing the actual first invite unavailable')

        source = SideShiftLive(Client(), flow.COMPANY)
        self.assertTrue(checks.signing_seen(source.read('chat1', ['U1']), self.contract()),
                        'The complete history establishes signing after this contract first went out')
        phase[0], consumed[:] = 'failed', []
        return source, phase, consumed

    def test_AG01_gate_partial_before_unread_first_invite_survives_until_reminder(self):
        source, phase, consumed = self.partial_source()
        gate, sender = self.gate_for(source)
        result = gate.run(self.action(message_type='contract-reminder-1', fields={'First': 'Ada'}))
        self.assertEqual(consumed, ['reinvite', 'request1'], 'Request consumed; actual first invite not yet read')
        self.assertEqual(result.outcome, 'held', result.reasons)
        self.assertIn('no complete live read', result.reasons[0])
        self.assertEqual(sender.delivered, [], 'Incomplete history cannot authorize the first attempt')
        phase[0] = 'redacted'
        self.later_reminder(source)

    def test_AG01_flow_partial_before_unread_first_invite_survives_until_withdrawal(self):
        source, phase, consumed = self.partial_source()
        job = flow.Flow(SimpleNamespace(pages=lambda *a, **kw: [self.contract()]), source,
                        None, self.j, lambda cid: ('route1', 'person1'), now=lambda: NOW,
                        read_client=SimpleNamespace(pages=lambda *a, **kw: []))
        report = job.run()
        self.assertEqual(consumed, ['reinvite', 'request1'])
        self.assertTrue(any('no live read' in line for line in report), report)
        phase[0] = 'redacted'
        self.later_withdrawal(source)


class ApplicationsBeforeContractFailure(PersistenceCase):
    def failed_contract_batch(self, partial_applications=False):
        consumed, visited, failures = [], [], []
        application = dict(id='app-U1', programId=flow.CAMPAIGN, creator={'id': 'U1'},
                           status='pending', requestedAt=NOW.isoformat())

        class Applications:
            def pages(inner, path, **kwargs):
                self.assertEqual(path, '/applications')
                consumed.append(application)
                yield application
                if partial_applications:
                    raise OSError('later application page unavailable')

        class Contracts:
            def pages(inner, path, **kwargs):
                self.assertEqual(path, '/contracts')
                visited.append('C0')
                yield self.contract(id='C0', contractorId='U0', contractorName='Bea Example')
                failures.append('contracts page 2')
                raise OSError('later contract page containing C1 unavailable')

        class Chats:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    yield {'id': 'chat1', 'members': [flow.COMPANY, 'U1']}
                    return
                self.assertEqual(path, '/support-channels/chat1/messages')
                yield invite_row()

        source = SideShiftLive(Chats(), flow.COMPANY)
        job = flow.Flow(Contracts(), source, None, self.j, lambda cid: ('route1', 'person1'),
                        now=lambda: NOW, read_client=Applications())
        try:
            job.run()
        except OSError:
            pass  # This failure must not erase already-consumed requests for unvisited creators.
        self.assertEqual(consumed, [application], 'The real batch collector consumed positive signing for U1')
        self.assertEqual(visited, ['C0'])
        self.assertEqual(failures, ['contracts page 2'])
        # Application has been redacted; subsequent per-send reads are complete and empty.
        return source

    def test_AG02_complete_app_batch_survives_contract_pagination_failure_until_reminder(self):
        self.later_reminder(self.failed_contract_batch())

    def test_AG02_partial_app_batch_survives_contract_pagination_failure_until_withdrawal(self):
        self.later_withdrawal(self.failed_contract_batch(partial_applications=True))
