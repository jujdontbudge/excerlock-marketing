"""Offline safety/liveness assertions against the unmodified round-30 snapshot.

Run: python3 -m unittest discover -s out/tests -t .
No network or real model/access command is used.
"""
from types import SimpleNamespace

from gate import policy
from gate.tests.review3.support import Case, NOW, Live, conv, invite
from gate.tests.review4.support import flow
from gate.tests.review7.test_round7 import CheckedSender


class GuideRetryAfterDefiniteNoSend(Case):
    def test_AR01_closed_guide_attempt_must_not_be_escalated_as_open_forever(self):
        contract = self.contract(status='active')
        source = Live(conv(invite()))
        source.client = SimpleNamespace(pages=lambda *a, **kw: [
            dict(id='chat1', members=[flow.COMPANY, 'U1'])])

        class Sender(CheckedSender):
            def __init__(inner):
                super().__init__(source)
                inner.person_reads = 0

            def call(inner, tool, args):
                if tool == 'get_person':
                    inner.person_reads += 1
                    if inner.person_reads == 3:
                        # The initial preflight and post-review preflight work.
                        # Only the transport's final preflight has an outage,
                        # after intent was committed but before send_message.
                        raise OSError('temporary contacts outage')
                return super().call(tool, args)

        sender = Sender()
        gate = self.gate(types=policy.load(), source=source, sender=sender,
                         reader=lambda cid: dict(contract))
        gate.applications_reader = lambda uid: []
        job = flow.Flow(SimpleNamespace(pages=lambda *a, **kw: [dict(contract)]),
                        source, gate, self.j, lambda cid: ('route1', 'person1'),
                        now=lambda: NOW)
        key = 'gate:warmup-guide:sideshift:U1'
        first = job.run()
        self.assertEqual(sender.person_reads, 3, first)
        self.assertEqual(self.j.outcomes(key), ['dispatching', 'error'], first)
        self.assertFalse(self.j.spent(key), 'The real journal confirms this is retryable')
        self.assertEqual(sender.delivered, [])
        later = [job.run(), job.run()]
        guide = policy.render(policy.load()['warmup-guide'], {'First': 'Ada'})
        self.assertTrue(any(item['text'] == guide for item in sender.delivered),
                        f'A closed, definitely-unsent attempt permanently stops onboarding: {later}')
