"""Offline effect-boundary assertions; CX01 tests intentionally fail.

Real Gate, ContactsMCP parser/preflight/send, SideShiftLive, grant helper and
file-backed SQLite. Only remote responses, review verdicts and clocks are fake.
Run: python3 -m unittest discover -s out/tests -t .
"""
import subprocess
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate.tests.review84.test_round84 import Fixture
from gate.tests.review3 import support
import grant


class PremiumRecipientRetry(Fixture):
    def configure(self, option='a', *, unclear=False, replace_during_grant=True):
        self.setup_system(option=option, distinct=True)
        self.commands, self.grants, self.active = [], [], set()
        self.unclear, self.replace_during_grant = unclear, replace_during_grant
        self.email_row = dict(id='email1', senderUserId='U1',
            createdAt=(support.NOW - timedelta(hours=2)).isoformat(),
            content='original@example.com')
        self.rows['U1'].append(self.email_row)
        self.attach_granter('U1')

    def attach_granter(self, uid):
        worker = self.workers[uid]
        worker.gate.granter = lambda a: grant.grant(worker.journal,
            a.creator_key, a.fields['email'], 'offline review', runner=self.runner)

    def runner(self, argv, **kwargs):
        verb, email = argv[1:3]
        self.commands.append((verb, email))
        if verb == 'check':
            if self.unclear and email == 'original@example.com' and email in self.active:
                raise subprocess.TimeoutExpired(argv, 60)
            word = 'ACTIVE' if email in self.active else 'NONE'
        else:
            self.assertEqual(verb, 'grant')
            # This is the irreversible remote effect, observed independently of
            # the gate's eventual message outcome.
            self.grants.append(email)
            self.active.add(email)
            if email == 'original@example.com' and self.replace_during_grant:
                self.email_row.update(content='replacement@example.com', isEdited=True,
                                      updatedAt=self.clock.isoformat())
            if self.unclear and email == 'original@example.com':
                raise subprocess.TimeoutExpired(argv, 60)
            word = 'GRANTED'
        return SimpleNamespace(returncode=0, stdout=f'{word}: {email}', stderr='')

    def run_access(self, email, uid='U1'):
        return self.workers[uid].gate.run(replace(self.action_for(uid, 'app-access'),
                                                 fields={'email': email}))

    def restart_after_twenty_seconds(self):
        self.clock += timedelta(seconds=20)
        self.elapsed += 20
        self.workers['U1'] = self.worker('U1')
        self.attach_granter('U1')

    def test_CX01_confirmed_grant_without_message_must_not_fund_second_email(self):
        self.configure()
        first = self.run_access('original@example.com')
        self.assertEqual(first.outcome, 'held', first)
        self.assertIn('Premium granted, but the chat changed', str(first.reasons))
        self.assertTrue(self.j.premium_granted('sideshift:U1', 'original@example.com'))
        self.assertFalse(self.j.spent('gate:app-access:sideshift:U1'))
        self.assertEqual(self.deliveries, [])
        self.restart_after_twenty_seconds()
        second = self.run_access('replacement@example.com')
        self.assertLessEqual(len(self.grants), 1,
            f'One creator now owns two active Premium accounts: {self.active}; '
            f'first={first}; second={second}; commands={self.commands}')

    def test_CX01_unresolved_grant_must_not_be_retried_with_different_email(self):
        self.configure(unclear=True)
        first = self.run_access('original@example.com')
        self.assertEqual(first.outcome, 'held', first)
        self.assertFalse(self.j.premium_granted('sideshift:U1', 'original@example.com'))
        self.assertIn(('sideshift:U1', 'grant-intent'),
                      self.j.premium_owners('original@example.com'))
        self.assertEqual(self.deliveries, [])
        self.restart_after_twenty_seconds()
        second = self.run_access('replacement@example.com')
        self.assertLessEqual(len(self.grants), 1,
            f'An unresolved first grant did not stop a replacement grant: '
            f'{self.grants}; active={self.active}; first={first}; second={second}')

    def test_control_same_email_retry_checks_without_granting_twice(self):
        self.configure(replace_during_grant=False)
        original_runner = self.runner

        def runner(argv, **kwargs):
            result = original_runner(argv, **kwargs)
            if argv[1] == 'grant':
                self.paused.touch()
            return result

        worker = self.workers['U1']
        worker.gate.granter = lambda a: grant.grant(worker.journal,
            a.creator_key, a.fields['email'], 'offline review', runner=runner)
        first = self.run_access('original@example.com')
        self.assertEqual(first.outcome, 'held', first)
        self.assertEqual(self.deliveries, [])
        self.paused.unlink()
        self.restart_after_twenty_seconds()
        second = self.run_access('original@example.com')
        self.assertEqual(second.outcome, 'sent', second)
        self.assertEqual(self.grants, ['original@example.com'])

    def test_control_confirmed_message_spends_creator_key(self):
        self.configure(replace_during_grant=False)
        first = self.run_access('original@example.com')
        self.assertEqual(first.outcome, 'sent', first)
        self.email_row.update(content='replacement@example.com', isEdited=True,
                              updatedAt=self.clock.isoformat())
        self.restart_after_twenty_seconds()
        second = self.run_access('replacement@example.com')
        self.assertEqual(second.outcome, 'held', second)
        self.assertEqual(self.grants, ['original@example.com'])
        self.assertEqual(len(self.deliveries), 1)

    def assert_draft_contains_grants(self, option):
        self.configure(option=option)
        first = self.run_access('original@example.com')
        self.assertEqual(first.outcome, 'draft', first)
        self.email_row.update(content='replacement@example.com', isEdited=True,
                              updatedAt=self.clock.isoformat())
        self.restart_after_twenty_seconds()
        second = self.run_access('replacement@example.com')
        self.assertEqual(second.outcome, 'draft', second)
        self.assertEqual(self.grants, [])
        self.assertEqual(self.commands, [])
        self.assertEqual(self.deliveries, [])

    def test_control_option_b_makes_no_grants(self):
        self.assert_draft_contains_grants('b')

    def test_control_option_c_makes_no_grants(self):
        self.assert_draft_contains_grants('c')

    def test_control_unrelated_creators_may_each_receive_premium(self):
        self.configure(replace_during_grant=False)
        self.rows['U2'].append(dict(id='email2', senderUserId='U2',
            createdAt=(support.NOW - timedelta(hours=2)).isoformat(),
            content='other@example.com'))
        self.attach_granter('U2')
        first = self.run_access('original@example.com')
        second = self.run_access('other@example.com', 'U2')
        self.assertEqual((first.outcome, second.outcome), ('sent', 'sent'))
        self.assertEqual(self.grants, ['original@example.com', 'other@example.com'])

