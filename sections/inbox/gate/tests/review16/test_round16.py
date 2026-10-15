"""Offline counterexamples: required-behavior assertions intentionally fail.

Run: python3 -m unittest discover -s out/tests -t .
Real Flow, Gate, grant, SQLite journal and ContactsMCP boundary; fake remote services.
"""
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from gate.live import LiveReadError
from gate.model import IN
from gate.tests.review4.support import (
    Case, NOW, Live, conv, flow, grant, invite, msg, policy, withdraw,
)
from gate.tests.review7.test_round7 import CheckedSender


class PartialApplicationEvidence(Case):
    def observe_page_then_fail(self):
        yielded = []
        contract = self.contract(createdAt=(NOW - timedelta(hours=8)).isoformat())
        application = dict(id='request1', programId=flow.CAMPAIGN, creator={'id': 'U1'},
                           status='pending', requestedAt=NOW.isoformat())

        def pages(path):
            self.assertEqual(path, '/applications')
            yielded.append(application)
            yield application
            raise OSError('next application page unavailable')

        class Source(Live):
            client = SimpleNamespace(pages=lambda path: [
                {'id': 'chat1', 'members': [flow.COMPANY, 'U1']}])

            def read(inner, *a, **kw):
                raise LiveReadError('chat unavailable')

        job = flow.Flow(SimpleNamespace(pages=lambda *a, **kw: [contract]), Source(),
                        None, self.j, lambda cid: ('route1', 'person1'), now=lambda: NOW,
                        read_client=SimpleNamespace(pages=pages))
        report = job.run()
        self.assertEqual(yielded, [application])
        self.assertTrue(any('handle requests could not be read' in r for r in report), report)
        self.assertTrue(any('no live read' in r for r in report), report)

    def test_AD01_partial_application_read_survives_before_later_reminder(self):
        self.observe_page_then_fail()
        # That already-observed request is subsequently redacted. Six hours later,
        # a complete empty read must not erase positive evidence from the earlier page.
        source = Live(conv(invite(at=NOW - timedelta(hours=7))))
        sender = CheckedSender(source)
        gate = self.gate(types=policy.load(), source=source, sender=sender,
                         reader=lambda cid: self.contract())
        gate.applications_reader = lambda uid: []
        gate.now = lambda: NOW + timedelta(hours=6)
        result = gate.run(self.action(message_type='contract-reminder-2', fields={'First': 'Ada'}))
        self.assertEqual(sender.delivered, [],
                         f'Flow consumed a positive application page six hours earlier; reminder {result.outcome}')

    def test_AD01_partial_application_read_survives_before_later_withdrawal(self):
        self.observe_page_then_fail()
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        result = withdraw.withdraw('C1', lambda cid: self.contract(),
                                   lambda: conv(invite(at=NOW - timedelta(hours=7))),
                                   self.j, 'sideshift:U1', NOW + timedelta(hours=33), writer, lambda: [])
        self.assertEqual(writes, [],
                         f'Flow consumed a positive application page 33 hours earlier; withdrawal {result}')


class PremiumConfirmationOrigin(Case):
    def test_AD02_active_check_age_includes_ownership_commit_before_granter_returns(self):
        clock, armed, stalled, checks, entitlement, deliveries = [1000.0], [False], [], [], ['ACTIVE'], []
        current = self.contract(status='active')
        connection = self.j.conn

        class SlowCommit:
            def execute(inner, sql, *args):
                if sql == 'COMMIT' and armed[0]:
                    armed[0] = False
                    stalled.append(clock[0])
                    entitlement[0] = 'NONE'  # captain revokes at the start of storage latency
                    clock[0] += 120.0
                return connection.execute(sql, *args)

            def __getattr__(inner, name):
                return getattr(connection, name)

        self.j.conn = SlowCommit()

        def runner(argv, **kwargs):
            self.assertEqual(argv[1], 'check', 'Refreshing evidence must never re-grant')
            checks.append((clock[0], entitlement[0]))
            armed[0] = True
            return SimpleNamespace(returncode=0, stdout=f'{entitlement[0]}: ada@example.com', stderr='')

        source = Live(conv(invite(), msg('email', 'ada@example.com', direction=IN)))

        class Sender(CheckedSender):
            def call(inner, tool, args):
                if tool == 'send_message':
                    deliveries.append((clock[0], entitlement[0]))
                return super().call(tool, args)

        sender = Sender(source)
        t = policy.load()['app-access']
        gate = self.gate(types={t.id: t}, source=source, sender=sender, reader=lambda cid: dict(current))
        gate.applications_reader = lambda uid: []
        gate.now = lambda: NOW + timedelta(seconds=clock[0] - 1000.0)
        gate.granter = lambda action: grant.grant(self.j, action.creator_key, action.fields['email'],
                                                 'offline creator', runner=runner)
        gate.entitlement = lambda email: grant.active(email, runner=runner)  # same wiring as production
        with patch('time.monotonic', side_effect=lambda: clock[0]):
            result = gate.run(self.action(message_type=t.id, fields={'email': 'ada@example.com'},
                                         contract=dict(current)))
        self.assertEqual(stalled, [1000.0], 'Must stall the real settlement transaction COMMIT')
        self.assertEqual(clock[0], 1120.0)
        self.assertEqual(checks[0], (1000.0, 'ACTIVE'))
        self.assertEqual(entitlement[0], 'NONE')
        self.assertEqual(deliveries, [],
                         f'Entitlement confirmation is 120s old; {result.outcome}, checks={checks}, delivery={deliveries}')
