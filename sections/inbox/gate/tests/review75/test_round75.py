"""Offline required-behavior assertions; real Flow, Gate, SideShiftLive and ContactsMCP.

Only service responses, the clock and the SEND verdict are faked.
"""
from dataclasses import replace
from datetime import timedelta

from gate import checks
from gate.live import REQUEST_NOTICE_EXACT
from gate.tests.review3.support import Case, NOW
from gate.tests.review35 import test_round35 as fixtures


PROSE = ('📨 Requested handle @ada (tiktok) for this contract.\n\n'
         "I'll check your account tomorrow.")


class CompanyDeliveryActivity(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def exercise(self, *, option='a', vanished=False, captain=False,
                 notice_prefix=True, recent=True):
        self.setup_flow()
        if option == 'b':
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        elif option == 'c':
            scheduled = {'contract-reminder-1', 'contract-reminder-2',
                         'warmup-guide', 'ask-app-email'}
            self.g.types = {k: t if k in scheduled else replace(t, mode='draft')
                            for k, t in self.g.types.items()}
        row = dict(id='api-reply', sender='Excerlock',
                   createdAt=(NOW - timedelta(hours=10)).isoformat(),
                   content="I'll check your account tomorrow.")
        if captain:
            row['senderUserId'] = fixtures.flow.COMPANY
        self.rows.append(row)
        self.clock = NOW - timedelta(minutes=30 if recent else 270)
        self.source.read('chat1', ['U1'])
        self.clock = NOW - timedelta(minutes=15 if recent else 240)
        row.update(content=PROSE if notice_prefix else "I'll check your accounts tomorrow.",
                   isEdited=True, updatedAt=self.clock.isoformat())
        current = self.source.read('chat1', ['U1'])
        edited = next(m for m in current.messages if m.id == row['id'])
        self.assertEqual(edited.direction, 'out')
        self.assertEqual(edited.author, 'captain' if captain else 'company')
        self.assertEqual(edited.kind, 'handle_request' if notice_prefix else 'text')
        self.assertFalse(REQUEST_NOTICE_EXACT.fullmatch(edited.text.strip()))
        self.assertNotIn(row['id'], checks.unexplained_changes(self.j.events('sideshift:U1')))
        self.assertFalse(checks.signing_notice(edited))
        if vanished:
            self.rows.remove(row)
        self.clock = NOW
        report = self.job.run()
        self.assertFalse(any('error ' in line for line in report), report)
        return report

    def test_CK02_automatic_reminder_must_respect_recent_company_prose_edit(self):
        report = self.exercise()
        self.assertEqual(self.sender.delivered, [], report)

    def test_CK02_mixed_reminder_must_respect_recent_company_prose_edit(self):
        report = self.exercise(option='c')
        self.assertEqual(self.sender.delivered, [], report)

    def test_CK02_removed_company_prose_edit_must_keep_gap(self):
        report = self.exercise(vanished=True)
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_captain_authored_prefix_holds(self):
        report = self.exercise(captain=True)
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('min gap 180' in line for line in report), report)

    def test_control_company_prose_without_notice_prefix_holds(self):
        report = self.exercise(notice_prefix=False)
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('min gap 180' in line for line in report), report)

    def test_control_all_drafts_contains_send(self):
        report = self.exercise(option='b')
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_old_company_prose_allows_reminder(self):
        report = self.exercise(recent=False)
        self.assertEqual(len(self.sender.delivered), 1, report)


class RecycledRepostInvite(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def exercise(self, *, option='a', reminder=False, vanished=False,
                 current_edit=False, near_approval=True):
        from types import SimpleNamespace
        self.setup_flow()
        scheduled = {'contract-reminder-1', 'contract-reminder-2',
                     'warmup-guide', 'ask-app-email'}
        self.g.types = {k: replace(t, mode='draft') if option == 'b' or
                        (option == 'c' and k not in scheduled) else t
                        for k, t in self.g.types.items()}
        self.rows[0]['createdAt'] = (NOW - timedelta(hours=7 if reminder else 40)).isoformat()
        # A genuine old approval and the automatic repost for an EARLIER contract.
        approval = dict(id='old-approval', sender='Excerlock',
                        createdAt=(NOW - timedelta(hours=100 if near_approval else 102)).isoformat(),
                        content='✅ Your handle @ada (instagram) was approved for ExcerLock.')
        recycled = dict(id='old-repost', sender='Excerlock',
                        createdAt=(NOW - timedelta(hours=99.5)).isoformat(),
                        content='https://app.sideshift.app/campaign-invite/C0')
        self.rows.extend([approval, recycled])
        self.clock = NOW - timedelta(minutes=30)
        self.source.read('chat1', ['U1'])
        self.clock = NOW - timedelta(minutes=15)
        recycled.update(content='https://app.sideshift.app/campaign-invite/C1', isEdited=True)
        if current_edit:
            recycled['updatedAt'] = self.clock.isoformat()
        self.source.read('chat1', ['U1'])
        bad = checks.unexplained_changes(self.j.events('sideshift:U1'))
        if current_edit:
            self.assertNotIn(recycled['id'], bad)
        else:
            self.assertIn(recycled['id'], bad)
        if vanished:
            self.rows.remove(recycled)
        self.writes = []
        self.job.write_client = SimpleNamespace(request=lambda *a, **kw:
            self.writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))
        self.clock = NOW
        report = self.job.run()
        self.assertFalse(any('error ' in line for line in report), report)
        return report

    def test_CK01_automatic_must_not_withdraw_recycled_invite_with_unknown_edit_time(self):
        report = self.exercise()
        self.assertEqual(self.writes, [], report)

    def test_CK01_drafts_must_not_withdraw_recycled_invite_with_unknown_edit_time(self):
        report = self.exercise(option='b')
        self.assertEqual(self.writes, [], report)

    def test_CK01_mixed_must_not_withdraw_recycled_invite_with_unknown_edit_time(self):
        report = self.exercise(option='c')
        self.assertEqual(self.writes, [], report)

    def test_CK01_removed_recycled_invite_must_keep_unknown_clock(self):
        report = self.exercise(vanished=True)
        self.assertEqual(self.writes, [], report)

    def test_CK01_automatic_must_not_remind_recycled_invite_with_unknown_edit_time(self):
        report = self.exercise(reminder=True)
        self.assertEqual(self.sender.delivered, [], report)

    def test_CK01_mixed_must_not_remind_recycled_invite_with_unknown_edit_time(self):
        report = self.exercise(reminder=True, option='c')
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_current_edit_time_preserves_new_invite(self):
        report = self.exercise(current_edit=True)
        self.assertEqual(self.writes, [], report)

    def test_control_approval_outside_repost_window_preserves_unknown_invite(self):
        report = self.exercise(near_approval=False)
        self.assertEqual(self.writes, [], report)

    def test_control_drafts_contain_recycled_invite_reminder(self):
        report = self.exercise(reminder=True, option='b')
        self.assertEqual(self.sender.delivered, [], report)
