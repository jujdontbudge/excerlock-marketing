"""Offline safety assertions. Run: python3 -m unittest discover -s out/tests -t .

Real live normalizer, Gate, ContactsMCP send/preflight, Flow and private SQLite.
Only service data and the full-chat review verdict are faked; no network.
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.live import SideShiftLive
from gate.review import payload
from gate.tests.review21.test_round21 import ReviewCase, raw_invite
from gate.tests.review4.support import NOW, flow, policy


class Round26(ReviewCase):
    def source(self, rows):
        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    return [dict(id='chat1', members=[flow.COMPANY, 'U1'])]
                self.assertEqual(path, '/support-channels/chat1/messages')
                return rows
        return SideShiftLive(Client(), flow.COMPANY)

    def draft_flow(self, source):
        contract = self.contract_for()
        contracts = SimpleNamespace(pages=lambda *a, **kw: [dict(contract)],
                                    request=lambda *a, **kw: {'data': dict(contract)})
        gate, sender = self.configured(source, contract)
        gate.types = {key: replace(t, mode='draft') for key, t in policy.load().items()}
        writes = []
        job = flow.Flow(contracts, source, gate, self.j, lambda chat: ('route1', 'person1'),
                        now=lambda: NOW, write_client=self.writer(writes),
                        read_client=SimpleNamespace(pages=lambda *a, **kw: []))
        report = job.run()
        self.assertEqual(sender.delivered, [])
        return writes, report

    def edited_attachment(self, invite_hours):
        photo = dict(id='photo1', createdAt=(NOW - timedelta(hours=25)).isoformat(),
                     senderUserId='U1', content='My draft', attachmentCount=1, isEdited=False)
        source = self.source([raw_invite(hours=invite_hours), photo])
        original = next(m for m in source.read('chat1').messages if m.id == 'photo1')
        self.j.event('sideshift:U1', 'attachment-reviewed', checks.mark(original), {'by': 'captain'})
        self.j.event('sideshift:U1', 'answered', checks.mark(original), {'by': 'captain'})
        original_review = payload(source.read('chat1'), 'candidate', 'contract-reminder-2')
        original_fingerprint = source.read('chat1').fingerprint
        # The provider exposes the changed edit flag but omits attachment ids and
        # updatedAt. A later job sees this stable new revision on every read.
        photo['isEdited'] = True
        self.assertNotEqual(source.read('chat1').fingerprint, original_fingerprint)
        # adapted 2026-10-15 (review BT02 fix): the reviewer now sees the edit ("edited": "unknown")
        self.assertIn('"edited": "unknown"', payload(source.read('chat1'), 'candidate', 'contract-reminder-2'))
        return source

    def test_AN01_edited_unidentified_attachment_requires_new_review_before_reminder(self):
        source = self.edited_attachment(invite_hours=30)
        gate, sender = self.configured(source, self.contract_for())
        result = self.reminder(gate, self.contract_for())
        self.assertEqual(sender.delivered, [],
                         f'Old look-at mark authorized an edited attachment: {result.outcome}: {result.reasons}')

    def test_AN01_edited_unidentified_attachment_blocks_all_draft_withdrawal(self):
        source = self.edited_attachment(invite_hours=40)
        writes, report = self.draft_flow(source)
        self.assertEqual(writes, [], f'Old look-at mark authorized rejection with unseen media: {report}')

    def test_AN02_quoted_approval_with_question_is_not_an_answered_system_event(self):
        source = self.source([
            raw_invite(hours=40),
            dict(id='question1', createdAt=(NOW - timedelta(hours=25)).isoformat(),
                 senderUserId='U1', content='✅ Your handle @ada on Instagram was approved for this contract. '
                                          'Does this mean I am signed or do I need to do anything else?'),
        ])
        question = source.read('chat1').messages[-1]
        self.assertEqual(question.direction, 'in')
        self.assertIn('?', question.text)
        self.assertFalse(checks.signing_seen(source.read('chat1'), self.contract_for()),
                         'Her quoted approval must not itself prove signing')
        writes, report = self.draft_flow(source)
        self.assertEqual(writes, [], f'Content-only classification erased her unanswered question: {report}')
