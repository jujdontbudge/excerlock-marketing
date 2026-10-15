"""Required-behavior assertions at the real send boundary; CM01 fails.

Only service responses, the clock and the review verdict are faked. No network.
Run: python3 -m unittest discover -s out/tests -t .
"""
from dataclasses import replace
from datetime import timedelta

from gate import checks
from gate.tests.review3.support import Case, NOW
from gate.tests.review35 import test_round35 as fixtures


class MediaNoticeExemption(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def exercise(self, *, notice='approval', option='a', vanished=False,
                 media=True, replacement=True, correct_clock=False, old=False,
                 plain_prose=False):
        self.setup_flow()
        scheduled = {'contract-reminder-1', 'contract-reminder-2',
                     'warmup-guide', 'ask-app-email'}
        self.g.types = {k: replace(t, mode='draft') if option == 'b' or
                        (option == 'c' and k not in scheduled) else t
                        for k, t in self.g.types.items()}
        if notice == 'approval':
            self.current['status'] = 'active'
            self.rows.append(self.raw('guide',
                'Warm-up guide https://docs.google.com/document/d/'
                '1guNLxDR65XXBlYbMOgHIeUw_aRi8cT8J3fSS71vNIEY/edit',
                NOW - timedelta(hours=5)))
            words = ('✅ Your handle @ada on instagram was approved for ExcerLock. '
                     'You can now accept the contract.')
            target = 'ask-app-email'
        else:
            # Another contract's invite must not alter C1's seven-hour clock.
            words = 'https://app.sideshift.app/campaign-invite/C0'
            target = 'contract-reminder-1'
        row = dict(id='notice-with-media', sender='Excerlock',
                   createdAt=(NOW - timedelta(hours=50)).isoformat(),
                   isEdited=True, updatedAt=(NOW - timedelta(hours=49)).isoformat(),
                   content='Account setup example.' if plain_prose else words,
                   attachments=[dict(id='file-A')] if media else [])
        self.rows.append(row)
        self.clock = NOW - timedelta(hours=5) if old else NOW - timedelta(minutes=30)
        self.source.read('chat1', ['U1'])
        self.clock += timedelta(minutes=15)
        if replacement and media:
            row['attachments'] = [dict(id='file-B')]
        if correct_clock:
            row['updatedAt'] = self.clock.isoformat()
        observed = self.source.read('chat1', ['U1'])
        current = next(m for m in observed.messages if m.id == row['id'])
        self.assertEqual(current.direction, 'out')
        self.assertEqual(current.author, 'company')
        bad = checks.unexplained_changes(self.j.events('sideshift:U1'))
        self.assertEqual(row['id'] in bad, bool(replacement and media and not correct_clock))
        if vanished:
            self.rows.remove(row)
        # Every change predates every final check by at least fifteen minutes.
        self.clock = NOW
        report = self.job.run()
        self.assertFalse(any('error ' in line for line in report), report)
        for delivery in self.sender.delivered:
            self.assertEqual(delivery['text'],
                self.g.types[target].text.replace('{First}', 'Ada'))
        return report

    def test_CM01_auto_email_request_must_obey_gap_after_notice_file_change(self):
        report = self.exercise()
        self.assertEqual(self.sender.delivered, [], report)

    def test_CM01_mixed_email_request_must_obey_gap_after_notice_file_change(self):
        report = self.exercise(option='c')
        self.assertEqual(self.sender.delivered, [], report)

    def test_CM01_removed_notice_file_change_must_retain_email_request_gap(self):
        report = self.exercise(vanished=True)
        self.assertEqual(self.sender.delivered, [], report)

    def test_CM01_auto_reminder_must_obey_gap_after_invite_file_change(self):
        report = self.exercise(notice='invite')
        self.assertEqual(self.sender.delivered, [], report)

    def test_CM01_mixed_reminder_must_obey_gap_after_invite_file_change(self):
        report = self.exercise(notice='invite', option='c')
        self.assertEqual(self.sender.delivered, [], report)

    def test_CM01_removed_invite_file_change_must_retain_reminder_gap(self):
        report = self.exercise(notice='invite', vanished=True)
        self.assertEqual(self.sender.delivered, [], report)

    def test_CM01_correct_clock_media_notice_must_also_obey_gap(self):
        report = self.exercise(correct_clock=True)
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_plain_approval_keeps_system_exemption(self):
        report = self.exercise(media=False)
        self.assertEqual(len(self.sender.delivered), 1, report)

    def test_control_plain_invite_keeps_system_exemption(self):
        report = self.exercise(notice='invite', media=False)
        self.assertEqual(len(self.sender.delivered), 1, report)

    def test_control_ordinary_prose_file_change_is_held(self):
        report = self.exercise(plain_prose=True)
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('min gap 30' in line for line in report), report)

    def test_control_drafts_contain_media_notice_send(self):
        report = self.exercise(option='b')
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('draft mode' in line or 'min gap 30' in line for line in report), report)

    def test_control_old_media_with_believable_clock_allows_send(self):
        report = self.exercise(old=True, correct_clock=True)
        self.assertEqual(len(self.sender.delivered), 1, report)
