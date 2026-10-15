"""Offline counterexamples. Assertions specify required behavior and intentionally fail.

Run: python3 -m unittest discover -s out/tests -t .
Real Flow, Gate, Journal, grant and ContactsMCP boundaries; fake remote services only.
"""
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from gate.model import IN
from gate.tests.review4.support import (
    Case, NOW, Live, conv, flow, grant, invite, msg, policy, withdraw,
)
from gate.tests.review7.test_round7 import CheckedSender


class FlowChatEvidence(Case):
    def read_signing_then_fail_route(self):
        contract = self.contract(createdAt=(NOW - timedelta(hours=8)).isoformat())
        notice = msg('request', '📨 Requested 2 handles for this contract.', direction=IN, at=NOW)
        source = Live(conv(invite(at=NOW - timedelta(hours=7)), notice))
        source.client = SimpleNamespace(pages=lambda path: [
            {'id': 'chat1', 'members': [flow.COMPANY, 'U1']}])
        reads = []
        real_read = source.read

        def read(*args, **kwargs):
            reads.append(1)
            return real_read(*args, **kwargs)

        source.read = read

        def route(chat_id):
            raise RuntimeError('contacts route lookup unavailable')

        job = flow.Flow(SimpleNamespace(pages=lambda *a, **kw: [contract]), source,
                        None, self.j, route, now=lambda: NOW,
                        read_client=SimpleNamespace(pages=lambda path: []))
        report = job.run()
        self.assertEqual(reads, [1], 'Flow must actually read the positive chat evidence')
        self.assertTrue(any('error RuntimeError' in line for line in report), report)
        self.assertIn('C1', self.j.flags('sideshift:U1', 'contract-pending'))

    def test_AC01_chat_signing_survives_route_failure_before_later_reminder(self):
        self.read_signing_then_fail_route()
        # The notice disappears. Six hours later, the other reminder becomes due.
        source = Live(conv(invite(at=NOW - timedelta(hours=7))))
        sender = CheckedSender(source)
        gate = self.gate(types=policy.load(), source=source, sender=sender,
                         reader=lambda cid: self.contract())
        gate.applications_reader = lambda uid: []
        gate.now = lambda: NOW + timedelta(hours=6)
        result = gate.run(self.action(message_type='contract-reminder-2', fields={'First': 'Ada'}))
        self.assertEqual(sender.delivered, [],
                         f'Flow read signing before a route failure; six hours later: {result.outcome}')

    def test_AC01_chat_signing_survives_route_failure_before_later_withdrawal(self):
        self.read_signing_then_fail_route()
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        result = withdraw.withdraw('C1', lambda cid: self.contract(),
                                   lambda: conv(invite(at=NOW - timedelta(hours=7))),
                                   self.j, 'sideshift:U1', NOW + timedelta(hours=33), writer, lambda: [])
        self.assertEqual(writes, [],
                         f'Flow read signing before a route failure; 33 hours later: {result}')


class PremiumEvidenceAge(Case):
    def test_AC02_stale_entitlement_cannot_authorize_premium_is_on_notification(self):
        clock, entitlement, checks, deliveries, reads = [1000.0], ['ACTIVE'], [], [], []
        current = self.contract(status='active')

        class Source(Live):
            def read(inner, *args, **kwargs):
                reads.append(clock[0])
                # Only the first post-grant read stalls. The final callback then refreshes all
                # SideShift/DNC evidence quickly, resetting its timer without refreshing Premium.
                if 'ada@example.com' in self.j.flags('sideshift:U1', 'premium-granted') and len(reads) == 4:
                    entitlement[0] = 'NONE'  # captain revokes it at the beginning of this slow read
                    clock[0] += 120.0
                return inner.conv

        class Sender(CheckedSender):
            def call(inner, tool, args):
                if tool == 'send_message':
                    deliveries.append((clock[0], entitlement[0]))
                return super().call(tool, args)

        def runner(argv, **kwargs):
            self.assertEqual(argv[1], 'check', 'An already active account must not be re-granted')
            checks.append((clock[0], entitlement[0]))
            return SimpleNamespace(returncode=0, stdout=f'{entitlement[0]}: ada@example.com', stderr='')

        source = Source(conv(invite(), msg('email', 'ada@example.com', direction=IN)))
        sender = Sender(source)
        t = policy.load()['app-access']
        gate = self.gate(types={t.id: t}, source=source, sender=sender, reader=lambda cid: dict(current))
        gate.applications_reader = lambda uid: []
        gate.now = lambda: NOW + timedelta(seconds=clock[0] - 1000.0)
        gate.granter = lambda action: grant.grant(self.j, action.creator_key, action.fields['email'],
                                                 'offline creator', runner=runner)
        with patch('time.monotonic', side_effect=lambda: clock[0]):
            result = gate.run(self.action(message_type=t.id, fields={'email': 'ada@example.com'},
                                         contract=dict(current)))
        self.assertEqual(entitlement[0], 'NONE', 'The test must revoke Premium during the slow read')
        self.assertEqual(clock[0], 1120.0)
        self.assertEqual(checks[0], (1000.0, 'ACTIVE'))
        self.assertEqual(deliveries, [],
                         f'Entitlement proof is 120s old and revoked, but {result.outcome}: {deliveries}')
