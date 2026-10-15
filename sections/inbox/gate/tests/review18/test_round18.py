"""Required safety assertions, intentionally failing on the reviewed code. No network.

Run: python3 -m unittest discover -s out/tests -t .
Real Flow, SideShiftLive, Gate, SQLite journal, and ContactsMCP send/preflight;
only remote service responses and the review verdict are faked.
"""
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.live import SideShiftLive
from gate.tests.review4.support import Case, NOW, flow, policy, withdraw
from gate.tests.review7.test_round7 import CheckedSender


def invite_row(cid='C1'):
    return dict(id=f'invite-{cid}', createdAt=(NOW - timedelta(hours=10)).isoformat(),
                senderUserId=flow.COMPANY,
                content=f'https://app.sideshift.app/campaign-invite/{cid}')


def request_row():
    return dict(id='request1', createdAt=NOW.isoformat(), senderUserId='U1',
                content='📨 Requested 2 handles for this contract.')


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
                         f'Already-consumed signing was forgotten six hours later: {result.outcome}')

    def later_withdrawal(self, source):
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        result = withdraw.withdraw('C1', lambda cid: self.contract(),
                                   lambda: source.read('chat1', ['U1']), self.j,
                                   'sideshift:U1', NOW + timedelta(hours=30), writer, lambda: [])
        self.assertEqual(writes, [],
                         f'Already-consumed signing was forgotten 30 hours later: {result}')


class FinalTransportPartialChat(PersistenceCase):
    def transport_read_then_fail(self, malformed=False):
        reads, consumed = [], []

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    yield {'id': 'chat1', 'members': [flow.COMPANY, 'U1']}
                    return
                self.assertEqual(path, '/support-channels/chat1/messages')
                reads.append(path)
                yield invite_row()
                if len(reads) == 3:  # Gate initial, Gate post-review, then ContactsMCP.send
                    consumed.append('request1')
                    yield request_row()
                    if malformed:
                        yield dict(id='bad-row', senderUserId='U1', content='No timestamp')
                    else:
                        raise OSError('later chat page unavailable')

        source = SideShiftLive(Client(), flow.COMPANY)
        gate, sender = self.gate_for(source)
        result = gate.run(self.action(message_type='contract-reminder-1', fields={'First': 'Ada'}))
        self.assertEqual(len(reads), 3, 'Must fail in the actual transport read, outside Gate._read')
        self.assertEqual(consumed, ['request1'])
        self.assertEqual(result.outcome, 'error', result.reasons)
        self.assertTrue(any('final live read failed' in why for why in result.reasons), result.reasons)
        self.assertEqual(sender.delivered, [], 'The incomplete attempt itself must not send')
        # Subsequent reads contain just the invite: the request has been redacted.
        return source

    def test_AF01_failed_final_transport_page_survives_before_later_reminder(self):
        self.later_reminder(self.transport_read_then_fail())

    def test_AF01_malformed_final_transport_row_survives_before_later_withdrawal(self):
        self.later_withdrawal(self.transport_read_then_fail(malformed=True))


class FlowPartialVariableCollision(PersistenceCase):
    def flow_reads_request_then_other_chat_fails(self, valid_partial_chat=False):
        consumed = []
        application = dict(id='app-U1', programId=flow.CAMPAIGN, creator={'id': 'U1'},
                           status='pending', requestedAt=NOW.isoformat())

        class Applications:
            def pages(inner, path, **kwargs):
                self.assertEqual(path, '/applications')
                consumed.append(application)
                yield application
                raise OSError('later application page unavailable')

        class Chats:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    yield {'id': 'chat0', 'members': [flow.COMPANY, 'U0']}
                    yield {'id': 'chat1', 'members': [flow.COMPANY, 'U1']}
                elif path == '/support-channels/chat0/messages':
                    if valid_partial_chat:
                        yield invite_row('C0')
                    raise OSError('another creator chat unavailable')
                else:
                    self.assertEqual(path, '/support-channels/chat1/messages')
                    yield invite_row()

        contracts = [self.contract(id='C0', contractorId='U0', contractorName='Bea Example'),
                     self.contract()]
        source = SideShiftLive(Chats(), flow.COMPANY)
        job = flow.Flow(SimpleNamespace(pages=lambda *a, **kw: contracts), source,
                        None, self.j, lambda cid: ('route1', 'person1'), now=lambda: NOW,
                        read_client=Applications())
        report = job.run()
        self.assertEqual(consumed, [application], 'Actual Flow collector must have read U1 signing')
        self.assertTrue(any('handle requests could not be read' in r for r in report), report)
        self.assertTrue(any('no live read' in r for r in report), report)
        # The application is redacted before the later operation; current reads are complete/empty.
        return source

    def test_AF02_no_partial_chat_cannot_erase_other_creator_application_before_reminder(self):
        self.later_reminder(self.flow_reads_request_then_other_chat_fails())

    def test_AF02_valid_partial_chat_cannot_erase_other_creator_application_before_withdrawal(self):
        self.later_withdrawal(self.flow_reads_request_then_other_chat_fails(valid_partial_chat=True))


class PartialChatOrdering(PersistenceCase):
    def test_AF03_partial_history_keeps_first_invite_semantics_before_later_withdrawal(self):
        # Valid reverse-chronological service rows. Complete reads sort these; partial reads do not.
        reinvite = {**invite_row(), 'id': 'reinvite',
                    'createdAt': (NOW - timedelta(hours=7)).isoformat()}
        request = {**request_row(), 'createdAt': (NOW - timedelta(hours=8)).isoformat()}
        rows = [reinvite, request, invite_row()]
        phase, consumed = ['complete'], []

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    yield {'id': 'chat1', 'members': [flow.COMPANY, 'U1']}
                    return
                self.assertEqual(path, '/support-channels/chat1/messages')
                for row in rows:
                    if phase[0] != 'redacted' or row['id'] != 'request1':
                        consumed.append(row['id'])
                        yield row
                if phase[0] == 'failed':
                    raise OSError('later page unavailable')

        source = SideShiftLive(Client(), flow.COMPANY)
        self.assertTrue(checks.signing_seen(source.read('chat1', ['U1']), self.contract()),
                        'Exactly these valid rows prove signing when the read completes')
        phase[0], consumed[:] = 'failed', []
        gate, sender = self.gate_for(source)
        result = gate.run(self.action(message_type='contract-reminder-1', fields={'First': 'Ada'}))
        self.assertEqual(consumed, ['reinvite', 'request1', 'invite-C1'])
        self.assertEqual(result.outcome, 'held', result.reasons)
        self.assertIn('no complete live read', result.reasons[0])
        self.assertEqual(sender.delivered, [])
        phase[0] = 'redacted'
        self.later_withdrawal(source)
