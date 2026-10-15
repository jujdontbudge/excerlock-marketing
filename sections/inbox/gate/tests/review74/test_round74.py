"""Offline service fakes; real Flow, Gate, ContactsMCP and SQLite effects.

Assertions state required behavior. No production source changes or network.
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.live import classify
from gate.tests.review3.support import Case, NOW
from gate.tests.review35 import test_round35 as fixtures


NOTICE = '📨 Requested handle @ada (tiktok) for this contract.'
OLD = NOTICE.replace('Requested handle', 'Requested  handle')


class SigningFormattingTransition(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def exercise(self, *, option='a', reminder=False, vanished=False,
                 current_clock=False, distinct_words=False, unchanged=False):
        self.setup_flow()
        automatic = {'contract-reminder-1', 'contract-reminder-2',
                     'warmup-guide', 'ask-app-email'}
        self.g.types = {k: replace(t, mode='draft') if option == 'b' or
                        (option == 'c' and k not in automatic) else t
                        for k, t in self.g.types.items()}
        self.rows[0]['createdAt'] = (NOW - timedelta(hours=7 if reminder else 40)).isoformat()
        invitation = self.rows.pop(0)
        row = dict(id='creator-note', senderUserId='U1',
                   createdAt=(NOW - timedelta(hours=120)).isoformat(),
                   isEdited=True, updatedAt=(NOW - timedelta(hours=110)).isoformat(),
                   content=NOTICE if unchanged else ('Earlier note.' if distinct_words else OLD))
        self.rows.append(row)
        self.writes = []
        self.job.write_client = SimpleNamespace(request=lambda *a, **kw:
            self.writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))
        if not unchanged and not distinct_words:
            self.assertEqual(classify(row['content']), 'text')
            self.assertEqual(' '.join(OLD.split()), NOTICE)
        self.clock = NOW - timedelta(hours=100)
        self.source.read('chat1', ['U1'])
        self.rows.insert(0, invitation)
        self.clock = NOW - timedelta(minutes=30)
        self.source.read('chat1', ['U1'])
        self.assertTrue(any(e['kind'] == 'msg-last'
                            and e['ref'].startswith('creator-note#')
                            and checks.ts(e['at']) == self.clock
                            for e in self.j.events('sideshift:U1')))
        self.clock = NOW - timedelta(minutes=15)
        row.update(content=NOTICE,
                   updatedAt=(self.clock if current_clock else NOW - timedelta(hours=80)).isoformat())
        self.source.read('chat1', ['U1'])
        self.assertEqual(classify(row['content']), 'handle_request')
        if vanished:
            self.rows.remove(row)
        self.clock = NOW
        report = self.job.run()
        self.assertFalse(any('error ' in line for line in report), report)
        return report

    def test_CJ01_auto_must_not_withdraw_after_new_signing_notice(self):
        report = self.exercise()
        self.assertEqual(self.writes, [], report)

    def test_CJ01_drafts_must_not_withdraw_after_new_signing_notice(self):
        report = self.exercise(option='b')
        self.assertEqual(self.writes, [], report)

    def test_CJ01_mixed_must_not_withdraw_after_new_signing_notice(self):
        report = self.exercise(option='c')
        self.assertEqual(self.writes, [], report)

    def test_control_removed_row_retains_unanswered_old_note(self):
        report = self.exercise(vanished=True)
        self.assertEqual(self.writes, [], report)

    def test_CJ01_auto_must_not_remind_after_new_signing_notice(self):
        report = self.exercise(reminder=True)
        self.assertEqual(self.sender.delivered, [], report)

    def test_CJ01_mixed_must_not_remind_after_new_signing_notice(self):
        report = self.exercise(reminder=True, option='c')
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_current_edit_clock_stops_withdrawal(self):
        report = self.exercise(current_clock=True)
        self.assertEqual(self.writes, [], report)

    def test_control_distinct_words_stops_withdrawal(self):
        report = self.exercise(distinct_words=True)
        self.assertEqual(self.writes, [], report)

    def test_control_actual_precontract_notice_allows_withdrawal(self):
        report = self.exercise(unchanged=True)
        self.assertEqual(len(self.writes), 1, report)

    def test_control_drafts_contain_reminder(self):
        report = self.exercise(option='b', reminder=True)
        self.assertEqual(self.sender.delivered, [], report)
