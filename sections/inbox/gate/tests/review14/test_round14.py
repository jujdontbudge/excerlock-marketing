"""Offline counterexamples; assertions specify required behavior and fail on this snapshot.

Run: python3 -m unittest discover -s out/tests -t .
Real gate, Flow, journal, grant, parser and transport; fake services and private SQLite only.
"""
import json
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from gate.live import LiveReadError
from gate.model import IN
from gate.tests.review4.support import Case, NOW, Live, conv, invite, msg, policy, flow, grant, withdraw
from gate.tests.review7.test_round7 import CheckedSender


class FlowObservations(Case):
    def failed_flow(self, active=False, ambiguous=False):
        contract = self.contract(status='active' if active else 'pending')
        application = {'id': 'req1', 'programId': flow.CAMPAIGN, 'creator': {'id': 'U1'},
                       'status': 'pending', 'requestedAt': NOW.isoformat()}

        class Source(Live):
            client = SimpleNamespace(pages=lambda path: [
                {'id': 'chat1', 'members': [flow.COMPANY, 'U1']},
                *([{'id': 'chat2', 'members': [flow.COMPANY, 'U1']}] if ambiguous else [])])

            def read(inner, *a, **kw):
                raise LiveReadError('chat service unavailable')

        job = flow.Flow(
            SimpleNamespace(pages=lambda *a, **kw: [contract]), Source(), None, self.j,
            lambda chat: ('route1', 'person1'), now=lambda: NOW,
            read_client=SimpleNamespace(pages=lambda path: [] if active else [application]))
        report = job.run()
        self.assertTrue(any(('2 SideShift chats' if ambiguous else 'no live read') in r for r in report), report)

    def later_reminder(self):
        source = Live(conv(invite(at=NOW - timedelta(hours=7))))
        sender = CheckedSender(source)
        gate = self.gate(types=policy.load(), source=source, sender=sender,
                         reader=lambda cid: self.contract())
        gate.applications_reader = lambda uid: []
        gate.now = lambda: NOW + timedelta(hours=6)
        result = gate.run(self.action(message_type='contract-reminder-2', fields={'First': 'Ada'}))
        self.assertEqual(sender.delivered, [],
                         f'Flow already read a signing request, but six hours later reminder {result.outcome}')

    def test_AB01_flow_application_survives_failed_chat_read(self):
        self.failed_flow()
        self.later_reminder()

    def test_AB01_flow_application_survives_ambiguous_chat_return(self):
        self.failed_flow(ambiguous=True)
        self.later_reminder()

    def test_AB01_flow_active_contract_survives_failed_chat_before_withdrawal(self):
        self.failed_flow(active=True)
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        result = withdraw.withdraw('C1', lambda cid: self.contract(),
                                   lambda: conv(invite(at=NOW - timedelta(hours=40))), self.j,
                                   'sideshift:U1', NOW + timedelta(hours=3), writer, lambda: [])
        self.assertEqual(writes, [], f'Flow read the active contract three hours earlier, yet {result}')


class PremiumCommitDeadline(Case):
    def test_AB02_slow_ownership_commit_cannot_grant_after_evidence_expires(self):
        clock, armed, stalled, calls = [1000.0], [False], [], []
        current = self.contract(status='active')
        connection = self.j.conn

        class SlowCommit:
            """Inject storage latency at the real settlement transaction's COMMIT, after fresh()."""
            def execute(inner, sql, *args):
                if sql == 'COMMIT' and armed[0]:
                    armed[0] = False
                    stalled.append(clock[0])
                    current['status'] = 'cancelled'
                    clock[0] += 11.0
                return connection.execute(sql, *args)

            def __getattr__(inner, name):
                return getattr(connection, name)

        self.j.conn = SlowCommit()

        def runner(argv, **kw):
            calls.append((argv[1], clock[0], current['status']))
            if argv[1] == 'check':
                armed[0] = True
                line = 'NONE: ada@example.com'
            else:
                line = 'GRANTED: ada@example.com'
            return SimpleNamespace(returncode=0, stdout=line, stderr='')

        source = Live(conv(invite(), msg('email', 'ada@example.com', direction=IN)))
        sender = CheckedSender(source)
        t = policy.load()['app-access']
        gate = self.gate(types={t.id: t}, source=source, sender=sender, reader=lambda cid: dict(current))
        gate.applications_reader = lambda uid: []
        gate.now = lambda: NOW + timedelta(seconds=clock[0] - 1000.0)
        gate.granter = lambda action: grant.grant(self.j, action.creator_key, action.fields['email'],
                                                 'offline creator', runner=runner)
        with patch('time.monotonic', side_effect=lambda: clock[0]):
            result = gate.run(self.action(message_type=t.id, fields={'email': 'ada@example.com'},
                                         contract=dict(current)))
        self.assertEqual(stalled, [1000.0], 'Test must stall the settlement COMMIT')
        self.assertEqual(sender.delivered, [], 'The post-grant contract check should stop the notification')
        self.assertEqual([c for c in calls if c[0] == 'grant'], [],
                         f'Grant launched after an 11-second COMMIT with cancelled contract; notification {result.outcome}')


class PersonIdentity(Case):
    def test_AB03_other_person_record_cannot_clear_dnc_for_recipient(self):
        source = Live()
        reads = []

        class Sender(CheckedSender):
            from gate.contacts import ContactsMCP
            call = ContactsMCP.call

            def _post(inner, body):
                tool, args = body['params']['name'], body['params']['arguments']
                if tool == 'get_person':
                    reads.append(args['person_id'])
                    # person1's tags are unavailable. The response explicitly identifies a different person.
                    result = {'id': 'person2', 'tags': []}
                else:
                    result = super().call(tool, args)
                return SimpleNamespace(text=json.dumps({'jsonrpc': '2.0', 'id': 1,
                    'result': {'content': [{'type': 'text', 'text': json.dumps(result)}]}}))

        sender = Sender(source)
        t = policy.load()['warmup-guide']
        gate = self.gate(types={t.id: t}, source=source, sender=sender,
                         reader=lambda cid: self.contract(status='active'))
        result = gate.run(self.action(message_type=t.id, fields={'First': 'Ada'},
                                     contract=self.contract(status='active')))
        self.assertTrue(reads)
        self.assertEqual(set(reads), {'person1'})
        self.assertEqual(sender.delivered, [],
                         f'Every get_person response names person2; person1 DNC is unknown, yet {result.outcome}')
