import unittest
"""Offline round-84 regression assertions. No production code is changed.

HTTP is forbidden by the inherited fixture; Contacts and SideShift use its fake
transport while their real readers, preflight, gate and journal execute.
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.tests.review3 import support
from gate.tests.review83 import test_round83 as previous
import grant


class Fixture(support.Case):
    # Reuse only the offline setup, not its inherited regression test methods.
    setup_system = previous.LinkedAccountDelivery.setup_system
    raw = previous.LinkedAccountDelivery.raw
    action_for = previous.LinkedAccountDelivery.action_for
    worker = previous.LinkedAccountDelivery.worker
    run_job = previous.LinkedAccountDelivery.run_job


class CrossAccountActivity(Fixture):
    def observe_recycled_manual_row(self, option='a', media=False):
        self.setup_system(option=option)
        self.workers['U1'].sender.preflight(self.action_for('U1'))
        row = self.raw('manual-old-row', 'Thanks, Ada.', support.NOW - timedelta(hours=4))
        if media:
            row['attachments'] = [{'id': 'old-file'}]
        self.rows['U1'].append(row)
        self.clock = support.NOW - timedelta(hours=1)
        self.workers['U1'].live.read('chat1', ['U1'])
        # The captain changes content now; upstream retains the old row date and
        # provides no edit metadata. Both revisions really are observed.
        self.clock = support.NOW - timedelta(seconds=20)
        if media:
            row['attachments'] = [{'id': 'new-file'}]
        else:
            row['content'] = 'Thanks, Ada. I will check that for you.'
        self.workers['U1'].live.read('chat1', ['U1'])
        self.assertIn('manual-old-row', checks.unexplained_changes(self.j.events('sideshift:U1')))
        # Twenty seconds AFTER the observation, beyond the accepted 10s window.
        self.clock = support.NOW
        self.rows['U2'].append(self.raw('old-guide', 'Warm-up guide: https://docs.google.com/document/d/' +
            support.flow.WARMUP_DOC + '/edit', support.NOW - timedelta(hours=5)))
        # Restart, retaining only real journal observations.
        self.workers['U2'] = self.worker('U2')

    def test_CT01_auto_email_request_must_respect_observed_alias_activity(self):
        self.observe_recycled_manual_row()
        report = self.run_job('U2')
        self.assertEqual(self.deliveries, [], report)

    def test_CT01_mixed_email_request_must_respect_observed_alias_activity(self):
        self.observe_recycled_manual_row(option='c')
        report = self.run_job('U2')
        self.assertEqual(self.deliveries, [], report)

    def test_CT01_replaced_file_on_alias_must_respect_gap(self):
        self.observe_recycled_manual_row(media=True)
        report = self.run_job('U2')
        self.assertEqual(self.deliveries, [], report)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_same_account_retains_unknown_activity_clock(self):
        self.observe_recycled_manual_row()
        d = self.workers['U1'].gate.run(self.action_for('U1', 'ask-app-email'))
        self.assertEqual(self.deliveries, [], str(d))
        self.assertIn('min gap', str(d.reasons))

    def test_control_drafts_contain_alias_gap_send(self):
        self.observe_recycled_manual_row(option='b')
        report = self.run_job('U2')
        self.assertEqual(self.deliveries, [], report)


class ChangingComponent(Fixture):
    def premium_action(self, uid):
        return replace(self.action_for(uid, 'app-access'), fields={'email': uid.lower() + '@example.com'})

    def changing_component(self, option='a', connected_before=False, unrelated=False):
        self.setup_system(option=option, distinct=True)
        self.grants, self.second = [], None
        for uid in ('U1', 'U2'):
            self.rows[uid].append(dict(id='email-' + uid,
                content=uid.lower() + '@example.com',
                createdAt=(support.NOW - timedelta(hours=2)).isoformat(), senderUserId=uid))
            worker = self.workers[uid]

            def runner(argv, uid=uid, **kwargs):
                verb, email = argv[1:3]
                if verb == 'check':
                    return SimpleNamespace(returncode=0, stdout='NONE: ' + email, stderr='')
                self.assertEqual(verb, 'grant')
                self.grants.append(email)
                if uid == 'U2':
                    self.assertGreaterEqual(self.elapsed, 20)
                    self.assertFalse(self.j.spent('gate:app-access:sideshift:U2'))
                    # U2's first irreversible grant is still in flight. Separate
                    # Gate/connection U1 must be blocked by the component lock.
                    # No message dispatch intent yet exists for U2.
                    self.second = self.workers['U1'].gate.run(self.premium_action('U1'))
                return SimpleNamespace(returncode=0, stdout='GRANTED: ' + email, stderr='')

            worker.gate.granter = lambda action, w=worker, r=runner: grant.grant(
                w.journal, action.creator_key, action.fields['email'], 'offline review', runner=r)

        # A third account U0 starts on person1. Observe its real membership;
        # U2 remains a separate component before it acquires its lock.
        self.handles['person1'] = ['U0', 'U1']
        self.workers['U1'].sender.preflight(self.premium_action('U1'))

        def connect():
            # One ordinary move: U0 leaves person1 for person2. Historical links
            # join both components while U1/person1 and U2/person2 stay valid.
            self.handles['person1'] = ['U1']
            self.handles['person2'] = ['U0', 'U2']
            self.workers['U2'].sender.preflight(self.premium_action('U2'))
            self.assertEqual(self.j.component_accounts('sideshift:U2'),
                             {'sideshift:U0', 'sideshift:U1', 'sideshift:U2'})

        if connected_before:
            connect()

        def review(*args):
            if not connected_before and not unrelated:
                connect()
            # Membership is durable twenty seconds before U2 authorizes a grant.
            # Subsequent final reads are fast and current, with no stale clocks.
            self.elapsed += 20
            self.clock += timedelta(seconds=20)
            return 'SEND', 'offline review', []

        self.workers['U2'].gate.reviewer = review
        return self.workers['U2'].gate.run(self.premium_action('U2'))

    def test_CT02_component_growth_must_not_allow_parallel_premium_grants(self):
        first = self.changing_component()
        self.assertLessEqual(len(self.grants), 1, (first, self.second, self.grants))

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_component_known_before_lock_serializes_grants(self):
        first = self.changing_component(connected_before=True)
        self.assertEqual(self.grants, ['u2@example.com'], (first, self.second))
        self.assertIn('being handled', str(self.second.reasons))

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_unrelated_people_may_each_get_premium(self):
        self.changing_component(unrelated=True)
        self.assertEqual(self.grants, ['u2@example.com', 'u1@example.com'])

    def test_control_all_drafts_contain_component_grant(self):
        first = self.changing_component(option='b')
        self.assertEqual(first.outcome, 'draft', str(first))
        self.assertEqual(self.grants, [])

    def test_control_mixed_drafts_contain_component_grant(self):
        first = self.changing_component(option='c')
        self.assertEqual(first.outcome, 'draft', str(first))
        self.assertEqual(self.grants, [])
