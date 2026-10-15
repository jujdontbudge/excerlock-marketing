"""Offline safety assertions. These fail against the reviewed source.

Run: python3 -m unittest discover -s out/tests -t .
Real SideShiftLive, Gate, ContactsMCP preflight/send, Flow and SQLite.
Only service responses and the review verdict are faked; no network.
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate.live import SideShiftLive
from gate.review import payload
from gate.tests.review21.test_round21 import ReviewCase, raw_invite
from gate.tests.review4.support import NOW, flow, policy


class InvalidDeletionFlag(ReviewCase):
    def source(self, invite_hours):
        rows = [raw_invite(hours=invite_hours),
                dict(id='question1', createdAt=(NOW - timedelta(hours=25)).isoformat(),
                     senderUserId='U1', content='Can you answer my payment question before I sign?',
                     isDeleted='false')]

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    return [dict(id='chat1', members=[flow.COMPANY, 'U1'])]
                self.assertEqual(path, '/support-channels/chat1/messages')
                return rows

        return SideShiftLive(Client(), flow.COMPANY)

    def test_AM01_string_false_cannot_hide_unanswered_question_from_reminder_and_reviewer(self):
        contract = self.contract_for()
        source = self.source(invite_hours=30)
        gate, sender = self.configured(source, contract)
        reviewed = []

        def review(conv, text, kind, facts):
            reviewed.append(payload(conv, text, kind, facts))
            return 'SEND', 'No unanswered question is visible in the review payload.', []

        gate.reviewer = review
        result = self.reminder(gate, contract)
        for data in reviewed:
            self.assertNotIn('payment question', data, 'Reproduction requires reviewer to lose the question too')
        self.assertEqual(sender.delivered, [],
                         f'Unvalidated deletion flag concealed a real question: {result.outcome}: {result.reasons}')

    def test_AM01_draft_flow_cannot_withdraw_when_string_false_hides_unanswered_question(self):
        contract = self.contract_for()
        source = self.source(invite_hours=40)
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
        self.assertEqual(writes, [], f'Unvalidated deletion flag authorized irreversible rejection: {report}')
