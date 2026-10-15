"""Offline counterexamples: assertions describe required behavior and currently fail.

Run: python3 -m unittest discover -s out/tests -t .
Real Gate, Journal and ContactsMCP logic; private journals and fake remote services only.
"""
import json
from datetime import timedelta
from types import SimpleNamespace

from gate.live import LiveReadError
from gate.tests.review4.support import Case, NOW, Live, conv, invite, policy, withdraw
from gate.tests.review7.test_round7 import CheckedSender


class DurableResourceReads(Case):
    def request(self):
        return {'id': 'req1', 'status': 'pending', 'requestedAt': NOW.isoformat()}

    def later_reminder(self, gate, sender):
        gate.now = lambda: NOW + timedelta(hours=6)
        gate.contract_reader = lambda cid: self.contract()
        gate.applications_reader = lambda uid: []
        result = gate.run(self.action(message_type='contract-reminder-2', fields={'First': 'Ada'}))
        self.assertEqual(sender.delivered, [],
                         f'An earlier successful resource read showed signing, but six hours later: {result.outcome}')

    def resource_observation(self, final=False, active=False):
        source = Live(conv(invite(at=NOW - timedelta(hours=7))))
        sender = CheckedSender(source)
        reads, app_reads = [], []

        def contract(cid):
            reads.append(1)
            if len(reads) == (2 if final else 1):
                if active:
                    return self.contract(status='active')
                raise RuntimeError('contract endpoint unavailable after successful applications read')
            return self.contract()

        def applications(uid):
            app_reads.append(1)
            # First: initial eligibility; second: after review; third: final transport callback.
            return [self.request()] if not active and len(app_reads) == (3 if final else 2) else []

        gate = self.gate(types=policy.load(), source=source, sender=sender, reader=contract)
        gate.applications_reader = applications
        first = gate.run(self.action(message_type='contract-reminder-1', fields={'First': 'Ada'}))
        self.assertNotEqual(first.outcome, 'sent')
        self.assertTrue(any(('changed to active' if active else 'could not re-read the contract') in reason
                            for reason in first.reasons), first.reasons)
        self.assertEqual(len(reads), 2 if final else 1)
        self.assertEqual(sender.delivered, [])
        self.later_reminder(gate, sender)

    def test_AA01_after_review_application_survives_failed_contract_read(self):
        self.resource_observation()

    def test_AA01_final_application_survives_failed_contract_read(self):
        self.resource_observation(final=True)

    def test_AA01_final_active_contract_survives_status_change_return(self):
        self.resource_observation(final=True, active=True)

    def test_AA01_withdraw_application_survives_failed_chat_read(self):
        def failed_chat():
            raise LiveReadError('history endpoint unavailable')

        # A successful applications read precedes an unsuccessful chat read. The job can fail/hold,
        # but must keep the positive application observation before the next scheduled run.
        try:
            withdraw.withdraw('C1', lambda cid: self.contract(), failed_chat, self.j,
                              'sideshift:U1', NOW, read_applications=lambda: [self.request()])
        except LiveReadError:
            pass
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        result = withdraw.withdraw('C1', lambda cid: self.contract(),
                                   lambda: conv(invite(at=NOW - timedelta(hours=40))), self.j,
                                   'sideshift:U1', NOW + timedelta(hours=3), writer, lambda: [])
        self.assertEqual(writes, [], f'Observed request disappeared before the next run, which then {result}')


class ContactsReadFailure(Case):
    def test_AA02_jsonrpc_person_error_cannot_authorize_automatic_send(self):
        """Valid JSON-RPC error, actual ContactsMCP.call parser and actual final preflight; no HTTP."""
        source = Live()

        class RPCSender(CheckedSender):
            # Use the production parser as well as production preflight/send.
            from gate.contacts import ContactsMCP
            call = ContactsMCP.call

            def _post(inner, body):
                tool = body['params']['name']
                if tool == 'get_person':
                    # The person may be DNC, but its record cannot be read. This is a protocol-level
                    # error, not result.isError; the parser silently turns it into {}.
                    return SimpleNamespace(text=json.dumps({'jsonrpc': '2.0', 'id': 1,
                        'error': {'code': -32603, 'message': 'person store unavailable'}}))
                result = super().call(tool, body['params']['arguments'])
                return SimpleNamespace(text=json.dumps({'jsonrpc': '2.0', 'id': 1,
                    'result': {'content': [{'type': 'text', 'text': json.dumps(result)}]}}))

        sender = RPCSender(source)
        t = policy.load()['warmup-guide']
        gate = self.gate(types={t.id: t}, source=source, sender=sender,
                         reader=lambda cid: self.contract(status='active'))
        result = gate.run(self.action(message_type=t.id, fields={'First': 'Ada'},
                                     contract=self.contract(status='active')))
        self.assertEqual(sender.delivered, [],
                         f'Every person/DNC read returned a JSON-RPC error, yet {result.outcome}')


if __name__ == '__main__':
    import unittest
    unittest.main()
