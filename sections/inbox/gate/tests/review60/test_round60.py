"""Offline required-behavior counterexamples against unchanged production sources."""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks, policy
from gate.live import LiveReadError
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review39 import test_round39 as record_fixtures


class Round60(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw
    run_record = record_fixtures.RevisionBoundaries.run_record

    def settle(self, mid):
        self.assertIn('marked answered', self.run_record('answered', mid))
        self.assertIn('marked attachment-reviewed', self.run_record('looked-at', mid))

    def unknown_creation(self, *, edited=True, known_creation=False):
        self.setup_flow()
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.writes = []
        self.job.write_client = SimpleNamespace(request=lambda *a, **kw:
            self.writes.append((a, kw)) or dict(id='C1', contractorId='U1', status='rejected'))
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        row = dict(id='unknown-creation', senderUserId='U1', content={'text': 'Still trying.'},
                   isEdited=edited, updatedAt=(self.clock - timedelta(hours=30)).isoformat())
        if known_creation:
            row['createdAt'] = (self.clock - timedelta(hours=31)).isoformat()
        self.rows.append(row)
        with self.assertRaises(LiveReadError):
            self.source.read('chat1', ['U1'])
        self.retained = [json.loads(e['data']) for e in self.j.events('sideshift:U1')
                         if e['kind'] == 'msg-seen' and json.loads(e['data'])['id'] == row['id']]
        self.rows.pop()
        self.settle(row['id'])
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BV01_valid_edit_time_cannot_erase_unknown_creation_activity(self):
        report = self.unknown_creation()
        self.assertEqual(self.writes, [], f'Unknown creation became ancient activity after content settlement: {report}; {self.retained}')

    def test_control_unknown_creation_without_edit_keeps_activity_hold(self):
        report = self.unknown_creation(edited=False)
        self.assertEqual(self.writes, [], report)
        self.assertTrue(any('last 24 hours' in x for x in report), report)

    def test_control_proven_old_creation_and_edit_can_be_settled(self):
        report = self.unknown_creation(known_creation=True)
        self.assertEqual(len(self.writes), 1, report)

    def bot_delivery(self, *, malformed=True, recent=True, drafts=False):
        self.setup_flow()
        if drafts:
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        row = dict(id='bot-delivery', sender='Excerlock',
                   createdAt=(self.clock - timedelta(minutes=1) if recent else
                              self.clock - timedelta(hours=4)).isoformat(),
                   content={'text': 'I will check this afternoon.'} if malformed else
                           'I will check this afternoon.')
        self.rows.append(row)
        if malformed:
            with self.assertRaises(LiveReadError):
                self.source.read('chat1', ['U1'])
        else:
            self.source.read('chat1', ['U1'])
        self.rows.pop()
        if malformed:
            self.settle(row['id'])
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BV02_unreadable_company_bot_delivery_must_count_for_gap(self):
        report = self.bot_delivery()
        self.assertEqual(self.sender.delivered, [], f'16-minute-old proven company bot delivery lost to unreadable fallback: {report}')

    def test_control_readable_company_bot_delivery_obeys_gap(self):
        report = self.bot_delivery(malformed=False)
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('min gap 180' in x for x in report), report)

    def test_control_old_settled_company_bot_delivery_allows_reminder(self):
        report = self.bot_delivery(recent=False)
        self.assertEqual(len(self.sender.delivered), 1, report)

    def test_control_draft_mode_contains_company_bot_gap_bypass(self):
        report = self.bot_delivery(drafts=True)
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('draft' in x or 'min gap' in x for x in report), report)

    def unreadable_duplicate(self, *, malformed=True, disappear=True, drafts=False):
        self.setup_flow()
        if drafts:
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        text = policy.render(self.g.types['contract-reminder-1'], {'First': 'Ada'})
        # The text, creation time and company ID are readable and proven. An
        # unrelated malformed sender display name forces the unreadable rescue.
        row = self.raw('manual-copy', text, self.clock - timedelta(hours=4))
        if malformed:
            row['senderName'] = {'name': 'Johan'}
        self.rows.append(row)
        if malformed:
            with self.assertRaises(LiveReadError):
                self.source.read('chat1', ['U1'])
        else:
            self.source.read('chat1', ['U1'])
        if disappear:
            self.rows.pop()
        if malformed:
            self.settle(row['id'])
        self.clock += timedelta(minutes=15)
        return self.job.run()

    def test_BV03_settling_unreadable_metadata_cannot_allow_duplicate_delivery(self):
        report = self.unreadable_duplicate()
        self.assertEqual(self.sender.delivered, [], f'Retained exact text with proven company ID was sent a second time: {report}')

    def test_control_readable_vanished_copy_prevents_duplicate(self):
        report = self.unreadable_duplicate(malformed=False)
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('already' in x or 'before' in x for x in report), report)

    def test_control_unreadable_copy_still_present_blocks_send(self):
        report = self.unreadable_duplicate(disappear=False)
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('no live read' in x for x in report), report)

    def test_control_draft_mode_contains_unreadable_duplicate(self):
        report = self.unreadable_duplicate(drafts=True)
        self.assertEqual(self.sender.delivered, [], report)
        # adapted 2026-10-15 (BV03 fix): the duplicate check now holds before the draft stage; either contains it
        self.assertTrue(any('draft' in x or 'held' in x for x in report), report)
