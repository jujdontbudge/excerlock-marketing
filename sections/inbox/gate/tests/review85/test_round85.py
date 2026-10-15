import unittest
"""Required behavior at real Flow/Gate/Contacts/grant boundaries, offline.

Only remote responses, model verdicts and clocks are fake. No production edits.
Run: python3 -m unittest discover -s out/tests -t .
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.live import LiveReadError
from gate.tests.review3 import support
from gate.tests.review84.test_round84 import Fixture
import grant


class OtherAccountInbound(Fixture):
    def evidence(self, option='a', *, media=False, distinct=False, answered=False):
        self.setup_system(option=option, distinct=distinct)
        self.workers['U1'].sender.preflight(self.action_for('U1'))
        row = dict(id='her-question', senderUserId='U1',
            createdAt=(support.NOW - timedelta(minutes=1)).isoformat(),
            content='I am trying to sign the invite on my other account. Can you help?')
        if media:
            row['attachments'] = [dict(id='screenshot')]
            row['content'] = 'Here is the error on my other account.'
        self.rows['U1'].append(row)
        self.clock = support.NOW - timedelta(seconds=20)
        seen = self.workers['U1'].live.read('chat1', ['U1'])
        m = next(m for m in seen.messages if m.id == row['id'])
        if answered:
            self.j.answer('sideshift:U1', checks.answer_mark(m), {'by': 'captain'})
        self.clock = support.NOW
        self.workers['U2'] = self.worker('U2')
        self.reviewed = []
        def review(conv, *args):
            self.reviewed.extend(m.text for m in conv.messages)
            return 'SEND', 'offline review of the supplied evidence', []
        self.workers['U2'].gate.reviewer = review

    def ask_email(self):
        self.rows['U2'].append(self.raw('old-guide',
            'https://docs.google.com/document/d/' + support.flow.WARMUP_DOC + '/edit',
            support.NOW - timedelta(hours=5)))
        return self.run_job('U2')

    def test_CU01_auto_must_hold_for_known_question_on_linked_account(self):
        self.evidence()
        report = self.ask_email()
        self.assertEqual(self.deliveries, [], (report, self.reviewed))

    def test_CU01_mixed_must_hold_for_known_question_on_linked_account(self):
        self.evidence(option='c')
        report = self.ask_email()
        self.assertEqual(self.deliveries, [], (report, self.reviewed))

    def test_CU01_guide_must_hold_for_known_unreviewed_linked_attachment(self):
        self.evidence(media=True)
        report = self.run_job('U2')
        self.assertEqual(self.deliveries, [], (report, self.reviewed))

    def withdrawal(self, option='a', *, distinct=False, same_account=False):
        self.evidence(option=option, distinct=distinct)
        if same_account:
            self.rows['U2'].append({**self.rows['U1'][-1], 'senderUserId': 'U2'})
        self.contracts['U2']['status'] = 'pending'
        self.rows['U2'][0]['createdAt'] = (support.NOW - timedelta(hours=37)).isoformat()
        worker = self.workers['U2']
        worker.job.fetch_contract = lambda cid: dict(self.contracts['U2'])
        self.withdrawals = []
        def request(method, path, **kwargs):
            self.withdrawals.append((method, path, kwargs))
            return dict(id='C2', contractorId='U2', status='rejected')
        worker.job.write_client = SimpleNamespace(request=request)
        return self.run_job('U2')

    def test_CU01_drafts_only_must_not_withdraw_while_linked_creator_needs_help(self):
        report = self.withdrawal(option='b')
        self.assertEqual(self.withdrawals, [], report)

    def test_CU01_auto_must_not_withdraw_while_linked_creator_needs_help(self):
        report = self.withdrawal()
        self.assertEqual(self.withdrawals, [], report)

    def test_CU01_mixed_must_not_withdraw_while_linked_creator_needs_help(self):
        report = self.withdrawal(option='c')
        self.assertEqual(self.withdrawals, [], report)

    def test_control_unrelated_question_does_not_block_email_request(self):
        self.evidence(distinct=True)
        report = self.ask_email()
        self.assertEqual(len(self.deliveries), 1, report)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_answered_linked_question_allows_email_request(self):
        self.evidence(answered=True)
        report = self.ask_email()
        self.assertEqual(len(self.deliveries), 1, report)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_same_account_question_holds(self):
        self.evidence()
        report = self.run_job('U1')
        self.assertEqual(self.deliveries, [], report)
        self.assertIn('asked something', str(report))

    def test_control_drafts_only_does_not_send_with_linked_question(self):
        self.evidence(option='b')
        report = self.ask_email()
        self.assertEqual(self.deliveries, [], report)

    def test_control_unrelated_question_does_not_block_due_withdrawal(self):
        report = self.withdrawal(option='b', distinct=True)
        self.assertEqual(len(self.withdrawals), 1, report)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_same_account_question_blocks_due_withdrawal(self):
        report = self.withdrawal(option='b', same_account=True)
        self.assertEqual(self.withdrawals, [], report)
        self.assertIn('waiting for an answer', str(report))


class UnreadableOtherAccountActivity(Fixture):
    def activity(self, option='a', *, changed=True, text=True):
        self.setup_system(option=option)
        self.workers['U1'].sender.preflight(self.action_for('U1'))
        row = self.raw('unreadable-captain', 'I will check that.' if text else '',
                       support.NOW - timedelta(hours=4))
        # A malformed source cannot be rescued into a normal Msg; our sender
        # identity and creation time are still usable veto evidence.
        row['source'] = ['native']
        row['attachments'] = [dict(id='file-A')]
        self.rows['U1'].append(row)
        def observe():
            try:
                self.workers['U1'].live.read('chat1', ['U1'])
            except LiveReadError as exc:
                self.assertIsNotNone(exc.partial)
            else:
                self.fail('fixture must exercise the unreadable-message path')
        self.clock = support.NOW - timedelta(hours=1)
        observe()
        if changed:
            self.clock = support.NOW - timedelta(seconds=20)
            row['attachments'] = [dict(id='file-B')]
            if text:
                row['content'] = 'I will check that for you.'
            observe()
            self.assertIn(row['id'], checks.unexplained_changes(self.j.events('sideshift:U1')))
        self.clock = support.NOW
        other = checks.with_history(support.conv(), self.j.events('sideshift:U1'))
        # Isolate the activity-clock defect from CU01: the captain has settled
        # every unreadable revision and looked at every file. A look/answer
        # does not erase when our outbound was edited.
        for m in other.messages:
            if m.author == 'us-unreadable':
                self.j.answer('sideshift:U1', checks.answer_mark(m), {'by': 'captain'})
                self.j.event('sideshift:U1', 'attachment-reviewed', checks.mark(m), {})
        self.assertEqual(checks.completeness(other, self.j.flags('sideshift:U1', 'attachment-reviewed')), [])
        self.assertEqual(checks.unanswered(other, self.j.answered('sideshift:U1')), [])
        if changed:
            self.assertTrue(checks.min_gap(other, self.clock, 30))
        self.rows['U2'].append(self.raw('old-guide',
            'https://docs.google.com/document/d/' + support.flow.WARMUP_DOC + '/edit',
            support.NOW - timedelta(hours=5)))
        self.workers['U2'] = self.worker('U2')
        return self.run_job('U2')

    def test_CU02_auto_must_respect_inferred_edit_on_unreadable_linked_outbound(self):
        report = self.activity()
        self.assertEqual(self.deliveries, [], report)

    def test_CU02_mixed_must_respect_inferred_edit_on_unreadable_linked_outbound(self):
        report = self.activity(option='c')
        self.assertEqual(self.deliveries, [], report)

    def test_CU02_attachment_only_linked_outbound_edit_must_count_for_gap(self):
        report = self.activity(text=False)
        self.assertEqual(self.deliveries, [], report)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_unchanged_old_unreadable_outbound_has_no_recent_gap(self):
        report = self.activity(changed=False)
        self.assertEqual(len(self.deliveries), 1, report)

    def test_control_draft_contains_unreadable_alias_gap(self):
        report = self.activity(option='b')
        self.assertEqual(self.deliveries, [], report)


class MergingDuringGrant(Fixture):
    def premium_action(self, uid):
        return replace(self.action_for(uid, 'app-access'), fields={'email': uid.lower() + '@example.com'})

    def overlap(self, option='a', *, merge=True, kind='app-access'):
        self.setup_system(option=option, distinct=True)
        self.grants, self.second = [], None
        for uid in ('U1', 'U2'):
            self.rows[uid].append(dict(id='email-' + uid,
                content=uid.lower() + '@example.com', senderUserId=uid,
                createdAt=(support.NOW - timedelta(hours=2)).isoformat()))
            worker = self.workers[uid]
            def runner(argv, uid=uid, **kwargs):
                verb, email = argv[1:3]
                if verb == 'check':
                    return SimpleNamespace(returncode=0, stdout='NONE: ' + email, stderr='')
                self.assertEqual(verb, 'grant')
                self.grants.append(email)
                if uid == 'U2':
                    self.assertIn(('sideshift:U2', 'grant-intent'),
                                  self.j.premium_owners('u2@example.com'))
                    self.assertFalse(self.j.spent('gate:app-access:sideshift:U2'))
                    self.assertIsNotNone(self.j.conn.execute(
                        'SELECT holder FROM reservations WHERE conversation_id=?',
                        ('component-lock:sideshift:U2',)).fetchone())
                    # U2's irreversible request is in flight, with no dispatching
                    # message intent yet. U9 is moved from person2 to person1,
                    # joining components without changing U1's minimum lock key.
                    if merge:
                        self.handles['person2'] = ['U2']
                        self.handles['person1'] = ['U9', 'U1']
                        self.workers['U1'].sender.preflight(self.premium_action('U1'))
                        self.assertEqual(self.j.component_accounts('sideshift:U1'),
                            {'sideshift:U9', 'sideshift:U1', 'sideshift:U2'})
                    self.elapsed += 20
                    self.clock += timedelta(seconds=20)
                    second = self.premium_action('U1') if kind == 'app-access' else self.action_for('U1', kind)
                    self.second = self.workers['U1'].gate.run(second)
                return SimpleNamespace(returncode=0, stdout='GRANTED: ' + email, stderr='')
            worker.gate.granter = lambda a, w=worker, r=runner: grant.grant(
                w.journal, a.creator_key, a.fields['email'], 'offline review', runner=r)
        # U9 starts in U2's component. After the merge, U1's new worker uses
        # component-lock:U1, bypassing U2's still-live component-lock:U2.
        self.handles['person2'] = ['U9', 'U2']
        self.workers['U2'].sender.preflight(self.premium_action('U2'))
        first = self.workers['U2'].gate.run(self.premium_action('U2'))
        return first

    def test_CU03_merge_must_not_allow_two_grants_while_original_effect_is_in_flight(self):
        first = self.overlap()
        self.assertLessEqual(len(self.grants), 1, (first, self.second, self.grants))

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_unrelated_workers_can_each_grant(self):
        first = self.overlap(merge=False)
        self.assertEqual(self.grants, ['u2@example.com', 'u1@example.com'], (first, self.second))

    def test_control_all_drafts_make_no_grant(self):
        first = self.overlap(option='b')
        self.assertEqual(self.grants, [], first)

    def test_control_mixed_drafts_make_no_grant(self):
        first = self.overlap(option='c')
        self.assertEqual(self.grants, [], first)
