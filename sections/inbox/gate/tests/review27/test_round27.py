"""Offline safety assertions; intentionally fail on the reviewed implementation.

Run: python3 -m unittest discover -s out/tests -t .
Real SideShiftLive, Gate, ContactsMCP preflight/send, Flow and private SQLite.
Only service responses and the review verdict are fakes; no network.
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.live import LiveReadError, SideShiftLive
from gate.review import payload
from gate.tests.review21.test_round21 import ReviewCase, raw_invite
from gate.tests.review4.support import NOW, flow, policy


class AttachmentIdentityValidation(ReviewCase):
    def source(self, rows):
        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    return [dict(id='chat1', members=[flow.COMPANY, 'U1'])]
                self.assertEqual(path, '/support-channels/chat1/messages')
                return rows
        return SideShiftLive(Client(), flow.COMPANY)

    def reviewed_photo(self, invite_hours, bad_identity):
        photo = dict(id='photo1', createdAt=(NOW - timedelta(hours=25)).isoformat(),
                     senderUserId='U1', content='My draft', attachmentCount=1, isEdited=True)
        if bad_identity == 'revision':
            # A blank string is not a usable revision timestamp. Unlike None or
            # '', it is truthy and so bypasses the new unidentifiable branch.
            photo['updatedAt'] = ' '
        else:
            # A boolean is not an immutable attachment identifier. The entire
            # attachment object is untrusted, even though it has an "id" key.
            photo['attachments'] = [dict(id=True, url='https://cdn.invalid/original.jpg')]
            photo['updatedAt'] = (NOW - timedelta(hours=25)).isoformat()
        source = self.source([raw_invite(hours=invite_hours), photo])
        original = source.read('chat1').messages[-1]
        for kind in ('attachment-reviewed', 'answered'):
            self.j.event('sideshift:U1', kind, checks.mark(original), {'by': 'captain'})
        old_payload = payload(source.read('chat1'), 'candidate', 'contract-reminder-2')
        if bad_identity == 'id':
            # The replacement predates the job and is stable on every later
            # read. Even its valid new revision time is ignored by the id path.
            photo['attachments'][0]['url'] = 'https://cdn.invalid/replacement.jpg'
            photo['updatedAt'] = (NOW - timedelta(hours=24, minutes=30)).isoformat()
        # For the revision-only row, a second replacement has no usable metadata:
        # isEdited is already True and updatedAt remains a blank sentinel.
        # adapted 2026-10-15 (review BT02 fix): the reviewer now sees edit times, so the payload may differ; the
        # deterministic attachment veto is what this test checks
        if bad_identity != 'id':
            self.assertEqual(payload(source.read('chat1'), 'candidate', 'contract-reminder-2'), old_payload,
                             'No media revision is exposed to the full-chat reviewer')
        return source

    def assert_reminder_held(self, bad_identity):
        try:
            source = self.reviewed_photo(30, bad_identity)
        except LiveReadError:
            return  # Rejecting the malformed row at normalization is also safe.
        gate, sender = self.configured(source, self.contract_for())
        result = self.reminder(gate, self.contract_for())
        self.assertEqual(sender.delivered, [],
                         f'Malformed attachment identity reused an old look: {result.outcome}: {result.reasons}')

    def assert_draft_withdrawal_held(self, bad_identity):
        try:
            source = self.reviewed_photo(40, bad_identity)
        except LiveReadError:
            return
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
        self.assertEqual(writes, [], f'Malformed identity authorized all-draft rejection: {report}')

    def test_AO01_blank_revision_cannot_authorize_reminder(self):
        self.assert_reminder_held('revision')

    def test_AO01_blank_revision_cannot_authorize_all_draft_withdrawal(self):
        self.assert_draft_withdrawal_held('revision')

    def test_AO01_boolean_attachment_id_cannot_authorize_reminder(self):
        self.assert_reminder_held('id')

    def test_AO01_boolean_attachment_id_cannot_authorize_all_draft_withdrawal(self):
        self.assert_draft_withdrawal_held('id')
