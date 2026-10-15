"""Offline regressions; assertions intentionally fail against this snapshot.

python3 -m unittest discover -s out/tests -t .
"""
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from gate import policy
from gate.model import Decision, IN
from gate.tests.review3.support import Case, NOW, Live, conv, invite, msg
from gate.tests.review4.support import flow, grant
from gate.tests.review7.test_round7 import CheckedSender


class PremiumCheckFreshness(Case):
    def test_AQ01_slow_none_check_cannot_authorize_grant_after_account_activated(self):
        clock, current, calls, mutations = [1000.0], ['NONE'], [], []
        contract = self.contract(status='active')
        source = Live(conv(invite(), msg('email', 'ada@example.com', direction=IN)))
        sender = CheckedSender(source)
        t = policy.load()['app-access']
        gate = self.gate(types={t.id: t}, source=source, sender=sender,
                         reader=lambda cid: dict(contract))
        gate.applications_reader = lambda uid: []
        gate.now = lambda: NOW + timedelta(seconds=clock[0] - 1000.0)

        def runner(argv, **kwargs):
            calls.append(tuple(argv[1:]))
            if argv[1] == 'check':
                observed = current[0]
                if len(calls) == 1:
                    # A check's response is delayed, within its real 60s timeout.
                    # The captain activates the account at the start of that delay.
                    current[0] = 'ACTIVE'
                    clock[0] += 45.0
                return SimpleNamespace(returncode=0, stdout=f'{observed}: ada@example.com', stderr='')
            self.assertEqual(argv[1], 'grant')
            mutations.append((clock[0], current[0]))
            current[0] = 'ACTIVE'
            return SimpleNamespace(returncode=0, stdout='GRANTED: ada@example.com', stderr='')

        gate.granter = lambda action: grant.grant(self.j, action.creator_key,
                                                 action.fields['email'], 'offline', runner=runner)
        gate.entitlement = lambda email: grant.active(email, runner=runner)
        with patch('time.monotonic', side_effect=lambda: clock[0]):
            result = gate.run(self.action(message_type=t.id, fields={'email': 'ada@example.com'},
                                         contract=dict(contract)))
        self.assertEqual(clock[0], 1045.0)
        self.assertEqual(calls[0], ('check', 'ada@example.com'))
        self.assertEqual(mutations, [],
                         f'45-second-old NONE caused a grant on an ACTIVE account: {mutations}; '
                         f'gate={result.outcome}, calls={calls}')


class OnboardingProgress(Case):
    def test_AQ02_confirmed_warmup_deleted_from_chat_must_not_block_email_request_forever(self):
        contract = self.contract(status='active')
        guide = policy.load()['warmup-guide']
        guide_text = policy.render(guide, {'First': 'Ada'})
        # A genuine, confirmed delivery, subsequently deleted at SideShift.
        source = Live(conv(invite(), msg('old-guide', guide_text, deleted=True)))
        sender = CheckedSender(source)
        gate = self.gate(types=policy.load(), source=source, sender=sender,
                         reader=lambda cid: dict(contract))
        gate.applications_reader = lambda uid: []
        action = self.action(message_type=guide.id, fields={'First': 'Ada'}, contract=contract)
        self.j.record(action, gate.key(guide, action),
                      Decision('sent', ['confirmed earlier'], guide_text, outbox_id='old-out'))
        # Keep the real journal's earlier delivery outside the gap window.
        gate.now = lambda: NOW + timedelta(days=2)
        source.client = SimpleNamespace(pages=lambda *a, **kw: [
            dict(id='chat1', members=[flow.COMPANY, 'U1'])])
        contracts = SimpleNamespace(pages=lambda *a, **kw: [dict(contract)])
        job = flow.Flow(contracts, source, gate, self.j, lambda cid: ('route1', 'person1'),
                        now=gate.now)
        reports = [job.run() for _ in range(2)]
        self.assertTrue(any(item['text'] == policy.render(policy.load()['ask-app-email'], {})
                            for item in sender.delivered),
                        f'Two scheduled runs never reach ask-app-email after confirmed warmup: {reports}')
