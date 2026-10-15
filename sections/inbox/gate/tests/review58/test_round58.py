"""Offline required-behavior counterexamples. Production sources are unchanged.

Real Flow, Gate, SideShiftLive, SQLite and ContactsMCP boundary; fake remote
responses, clock and SEND verdict. Run from the review root:
python3 -m unittest discover -s out/tests -t .
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.live import LiveReadError
from gate.review import payload
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review39 import test_round39 as record_fixtures


class Round58(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw
    run_record = record_fixtures.RevisionBoundaries.run_record

    def drafts_and_writer(self):
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.writes = []
        self.job.write_client = SimpleNamespace(request=lambda *a, **kw:
            self.writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))

    def settled_unreadable_activity(self, *, recent, malformed=True):
        self.setup_flow()
        self.drafts_and_writer()
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        row = dict(id='trying', senderUserId='U1',
                   createdAt=(self.clock - timedelta(hours=1 if recent else 30)).isoformat(),
                   content={'text': 'I am still trying to create my accounts.'} if malformed else
                           'I am still trying to create my accounts.')
        self.rows.append(row)
        if malformed:
            with self.assertRaises(LiveReadError):
                self.source.read('chat1', ['U1'])
        else:
            self.source.read('chat1', ['U1'])
        # Only the content is unreadable; the sender and creation time are
        # positive, recent evidence. The row then disappears upstream.
        self.rows.pop()
        self.assertIn('marked answered', self.run_record('answered', 'trying'))
        if malformed:
            self.assertIn('marked attachment-reviewed', self.run_record('looked-at', 'trying'))
        # Marks settle words/files, not the separate 24-hour activity rule.
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BT01_settling_unreadable_content_cannot_erase_recent_creation(self):
        report = self.settled_unreadable_activity(recent=True)
        self.assertEqual(self.writes, [],
            f'Known 75-minute-old creator activity became epoch-time fallback, allowing rejection: {report}')

    def test_control_readable_recent_creation_blocks_after_settlement(self):
        report = self.settled_unreadable_activity(recent=True, malformed=False)
        self.assertEqual(self.writes, [], report)
        self.assertTrue(any('last 24 hours' in line for line in report), report)

    def test_control_old_unreadable_content_can_be_settled(self):
        report = self.settled_unreadable_activity(recent=False)
        self.assertEqual(len(self.writes), 1, report)

    def recent_captain_content(self, *, edited, disappear=False, draft=False):
        self.setup_flow()
        if draft:
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.rows.append(self.raw('captain-update', 'I will check your accounts this afternoon.',
                                 self.clock - timedelta(hours=5) if edited else self.clock - timedelta(minutes=1)))
        if edited:
            self.rows[-1].update(isEdited=True, updatedAt=(self.clock - timedelta(minutes=1)).isoformat())
        self.source.read('chat1', ['U1'])
        if disappear:
            self.rows.pop()
        self.review_inputs = []

        def reviewer(conv, text, message_type, facts):
            self.review_inputs.append(json.loads(payload(conv, text, message_type, facts)))
            return 'SEND', 'The rendered reminder fits the supplied chat.', []

        self.g.reviewer = reviewer
        # All reads remain unchanged, 15 minutes after the edit was observed.
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BT02_recent_captain_edit_must_obey_minimum_gap(self):
        report = self.recent_captain_content(edited=True)
        self.assertEqual(self.sender.delivered, [],
            f'New captain content is only 16 minutes old, but the 180-minute gap used creation time: {report}')

    def test_BT02_vanished_captain_edit_must_obey_minimum_gap(self):
        report = self.recent_captain_content(edited=True, disappear=True)
        self.assertEqual(self.sender.delivered, [],
            f'Retained recent edit is also ignored by the journal gap: {report}')

    def test_control_same_recent_captain_content_in_new_row_holds(self):
        report = self.recent_captain_content(edited=False)
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('min gap 180' in line for line in report), report)

    def test_control_draft_mode_contains_captain_edit_send(self):
        report = self.recent_captain_content(edited=True, draft=True)
        self.assertEqual(self.sender.delivered, [], report)
        # adapted 2026-10-15 (BT02 fix): the gap now holds it before the draft stage; either contains it
        self.assertTrue(any('draft' in line or 'min gap' in line for line in report), report)

    def test_BT02_reviewer_must_see_time_of_current_content(self):
        report = self.recent_captain_content(edited=True)
        # adapted 2026-10-15 (BT02 fix): the gap now holds before review; check the payload the reviewer WOULD get
        self.assertTrue(any('min gap' in line for line in report), report)
        import json as _json
        from gate.review import payload as _payload
        shown = _json.loads(_payload(self.source.read('chat1'), 'candidate', 'contract-reminder-1'))
        row = next(m for m in shown['chat'] if m['text'].startswith('I will check'))
        # Either expose edit time explicitly or date the row by current content.
        self.assertIn(self.rows[-1]['updatedAt'], row.values(),
            f'The review is told only the five-hour-old creation time: {row}')

    def repeated_invite(self, *, new_row):
        self.setup_flow()
        first = self.job.run()
        self.assertEqual(len(self.sender.delivered), 1, first)
        # C1 -> OLD -> C1 on the same native row. Each change is observed; the
        # second C1 delivery is new content, introduced thirty minutes later.
        self.clock += timedelta(minutes=15)
        self.rows[0].update(content='https://app.sideshift.app/campaign-invite/OLD',
                            isEdited=True, updatedAt=self.clock.isoformat())
        self.source.read('chat1', ['U1'])
        self.clock += timedelta(minutes=15)
        if new_row:
            self.rows.append(self.raw('reinvite', 'https://app.sideshift.app/campaign-invite/C1', self.clock))
        else:
            self.rows[0].update(content='https://app.sideshift.app/campaign-invite/C1',
                                updatedAt=self.clock.isoformat())
        self.source.read('chat1', ['U1'])
        self.clock += timedelta(hours=6)
        return self.job.run()

    def test_BT03_reintroduced_link_needs_fresh_reminder_key(self):
        report = self.repeated_invite(new_row=False)
        self.assertEqual(len(self.sender.delivered), 2,
            f'New invite clock reached six hours, but the old native ID reuses a spent key: {report}')

    def test_control_new_row_reinvite_gets_fresh_reminder(self):
        report = self.repeated_invite(new_row=True)
        self.assertEqual(len(self.sender.delivered), 2, report)
        self.assertNotEqual(self.sender.delivered[0]['idempotency_key'],
                            self.sender.delivered[1]['idempotency_key'])
