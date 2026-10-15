"""Offline required-behavior assertions; production code is unchanged.

Real Flow, SideShiftLive, Gate, ContactsMCP send/preflight and SQLite.
Only service responses, time and the SEND reviewer are faked.
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.tests.review3.support import Case, NOW
from gate.tests.review35 import test_round35 as fixtures


class RepeatedObservation(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def exercise(self, *, option='a', reminder=False, vanished=False,
                 repeat=True, correct_clock=False, signing=False):
        self.setup_flow()
        automatic = {'contract-reminder-1', 'contract-reminder-2',
                     'warmup-guide', 'ask-app-email'}
        self.g.types = {k: replace(t, mode='draft') if option == 'b' or
                        (option == 'c' and k not in automatic) else t
                        for k, t in self.g.types.items()}
        self.writes = []
        self.job.write_client = SimpleNamespace(request=lambda *a, **kw:
            self.writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))
        if signing:
            self.rows[0]['createdAt'] = (NOW - timedelta(hours=40)).isoformat()
            later_invite = self.rows.pop(0)  # it did not exist at the earliest chat read
            row = dict(id='creator-note', senderUserId='U1',
                       createdAt=(NOW - timedelta(hours=120)).isoformat(),
                       isEdited=True, updatedAt=(NOW - timedelta(hours=110)).isoformat(),
                       content='')
            self.rows.append(row)
            claimed_age = 80   # older than the contract (60h), so excluded as signing
            first_age = 100
            new_words = '📨 Requested handle @ada (tiktok) for this contract.'
        else:
            row = self.rows[0]
            new_words = row['content']
            row.update(content='Earlier unrelated note.', isEdited=True,
                       createdAt=(NOW - timedelta(hours=100)).isoformat(),
                       updatedAt=(NOW - timedelta(hours=90)).isoformat())
            claimed_age = 7 if reminder else 40
            first_age = 80

        self.clock = NOW - timedelta(hours=first_age)
        self.source.read('chat1', ['U1'])
        def observations():
            return [e for e in self.j.events('sideshift:U1')
                    if e['kind'] == 'msg-seen' and json.loads(e['data'])['id'] == row['id']]
        old_count = len(observations())
        self.clock = NOW - timedelta(minutes=30)
        if signing:
            self.rows.insert(0, later_invite)
        if repeat:
            self.source.read('chat1', ['U1'])
            # The live reader really saw the old words again, but did not record
            # their latest observation time. No journal data is edited by this test.
            self.assertEqual(len(observations()), old_count)
        self.clock = NOW - timedelta(minutes=15)
        row.update(content=new_words,
                   updatedAt=(self.clock if correct_clock else
                              NOW - timedelta(hours=claimed_age)).isoformat())
        self.source.read('chat1', ['U1'])
        # adapted 2026-10-15 (CI01 fix): this premise documented the defect; the latest read of the old words is now
        # kept, so a stale claimed clock is flagged unless it is current or no later read contradicts it
        if repeat and not correct_clock:
            self.assertIn(row['id'], checks.unexplained_changes(self.j.events('sideshift:U1')))
        if vanished:
            self.rows.remove(row)
            if not self.rows:
                self.rows.append(self.raw('remaining', 'Thanks for your interest.',
                                          NOW - timedelta(hours=5)))
        self.clock = NOW
        report = self.job.run()
        self.assertFalse(any('error ' in line for line in report), report)
        return report

    def test_CI01_auto_must_not_withdraw_invite_seen_as_unrelated_thirty_minutes_ago(self):
        report = self.exercise()
        self.assertEqual(self.writes, [], report)

    def test_CI01_drafts_only_must_not_withdraw_new_invite(self):
        report = self.exercise(option='b')
        self.assertEqual(self.writes, [], report)

    def test_CI01_mixed_mode_must_not_withdraw_new_invite(self):
        report = self.exercise(option='c')
        self.assertEqual(self.writes, [], report)

    def test_CI01_removed_invite_must_preserve_latest_old_words_observation(self):
        report = self.exercise(vanished=True)
        self.assertEqual(self.writes, [], report)

    def test_CI01_must_not_remind_an_invite_at_most_thirty_minutes_old(self):
        report = self.exercise(reminder=True)
        self.assertEqual(self.sender.delivered, [], report)

    def test_CI01_new_signing_notice_must_stop_withdrawal(self):
        report = self.exercise(signing=True, option='b')
        self.assertEqual(self.writes, [], report)

    def test_CI01_removed_signing_notice_must_stop_withdrawal(self):
        report = self.exercise(signing=True, option='b', vanished=True)
        self.assertEqual(self.writes, [], report)

    def test_control_current_edit_clock_preserves_new_invite(self):
        report = self.exercise(correct_clock=True)
        self.assertEqual(self.writes, [], report)

    def test_control_no_repeated_observation_allows_old_edit_clock(self):
        report = self.exercise(repeat=False)
        self.assertEqual(len(self.writes), 1, report)

    def test_control_drafts_contain_premature_reminder(self):
        report = self.exercise(option='b', reminder=True)
        self.assertEqual(self.sender.delivered, [], report)
