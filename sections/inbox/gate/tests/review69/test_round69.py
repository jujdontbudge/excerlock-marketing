"""Offline regressions at the real Flow/Gate/SideShiftLive/ContactsMCP boundary.

Only remote responses, time and the SEND verdict are faked. Production sources
are unchanged. Run: python3 -m unittest discover -s out/tests -t .
"""
from dataclasses import replace
from datetime import timedelta

from gate import checks
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures


class CaptainNoticePrefix(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def exercise(self, *, notice_prefix=True, vanish=False, draft=False,
                 genuine_system=False, old=False):
        self.setup_flow()
        self.current['status'] = 'active'
        # She received the guide long ago; the scheduled next step is ask-app-email.
        self.rows.append(self.raw('guide',
            'Warm-up guide: https://docs.google.com/document/d/'
            '1guNLxDR65XXBlYbMOgHIeUw_aRi8cT8J3fSS71vNIEY/edit',
            self.clock - timedelta(hours=5)))
        prefix = '✅ Your handle @ada (instagram) was approved for ExcerLock.'
        prose = "I've checked the new accounts, thanks for setting them up."
        row = self.raw('captain-update',
            (prefix + '\n\n' + prose) if notice_prefix else prose,
            self.clock - timedelta(hours=2) if old else self.clock - timedelta(minutes=1))
        if genuine_system:
            row.pop('senderUserId')
            # adapted 2026-10-15 (CK02): a genuine notice has SideShift's real, exact shape
            row.update(sender='Excerlock', content='✅ Your handle @ada on instagram was approved for ExcerLock — Fitness & '
                                                   'Gym Girls ($300/mo + $1 CPM). You can now accept the contract.')
        self.rows.append(row)
        observed = self.source.read('chat1', ['U1'])
        update = next(m for m in observed.messages if m.id == row['id'])
        self.assertEqual(update.author, 'company' if genuine_system else 'captain')
        self.assertEqual(update.kind, 'handle_approved' if notice_prefix else 'text')
        if vanish:
            self.rows.pop()
        if draft:
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        # All source changes precede every decision by 15 minutes. No timing race.
        self.clock += timedelta(minutes=15)
        report = self.job.run()
        self.assertFalse(any('error ' in line for line in report), report)
        if self.sender.delivered:
            self.assertEqual(self.sender.delivered[0]['text'], self.g.types['ask-app-email'].text)
        return report

    def test_CE01_captain_prose_with_notice_prefix_must_obey_gap(self):
        report = self.exercise()
        self.assertEqual(self.sender.delivered, [],
            f'Scheduled email request sent 16 minutes after captain prose despite its 30-minute gap: {report}')

    def test_CE01_vanished_captain_prose_must_still_obey_gap(self):
        report = self.exercise(vanish=True)
        retained = checks.with_history(self.source.read('chat1'), self.j.events('sideshift:U1'))
        self.assertTrue(any(m.id == 'captain-update' and m.vanished for m in retained.messages))
        self.assertEqual(self.sender.delivered, [],
            f'Retained 16-minute-old captain delivery was exempted from the gap: {report}')

    def test_control_same_captain_prose_without_prefix_holds(self):
        report = self.exercise(notice_prefix=False)
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('min gap 30' in line for line in report), report)

    def test_control_genuine_sideshift_notice_keeps_system_exemption(self):
        report = self.exercise(genuine_system=True)
        self.assertEqual(len(self.sender.delivered), 1, report)

    def test_control_old_captain_prose_allows_scheduled_request(self):
        report = self.exercise(old=True)
        self.assertEqual(len(self.sender.delivered), 1, report)

    def test_control_draft_mode_contains_the_send(self):
        report = self.exercise(draft=True)
        self.assertEqual(self.sender.delivered, [], report)
        # adapted 2026-10-15 (CE01 fix): the gap now holds it before the draft stage; either contains it
        self.assertTrue(any('draft' in line or 'min gap' in line for line in report), report)
