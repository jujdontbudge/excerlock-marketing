"""Offline counterexamples against the unchanged round-31 snapshot.

Run: python3 -m unittest discover -s out/tests -t .
Real live normalizer, gate, SQLite journal, ContactsMCP boundary and withdrawal.
Only external responses, the clock and the review verdict are faked.
"""
from datetime import timedelta
from types import SimpleNamespace

from gate import policy
from gate.live import SideShiftLive
from gate.tests.review3.support import Case, NOW
from gate.tests.review4.support import flow, withdraw
from gate.tests.review7.test_round7 import CheckedSender


class MalformedSigningNotice(Case):
    def observed_notice_then_deleted(self, invite_hours):
        rows = [
            dict(id='invite1', createdAt=(NOW - timedelta(hours=invite_hours)).isoformat(),
                 senderUserId=flow.COMPANY,
                 content='https://app.sideshift.app/campaign-invite/C1'),
            dict(id='notice1', createdAt=(NOW - timedelta(hours=2)).isoformat(),
                 senderUserId='U1',
                 content='📨 Requested handle @ada.walks (tiktok) for this contract.',
                 attachmentCount='1'),
        ]
        consumed = []

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    return [dict(id='chat1', members=[flow.COMPANY, 'U1'])]
                self.assertEqual(path, '/support-channels/chat1/messages')
                consumed.extend(row['id'] for row in rows)
                return list(rows)

        source = SideShiftLive(Client(), flow.COMPANY)
        contract = self.contract(createdAt=(NOW - timedelta(hours=50)).isoformat())
        sender = CheckedSender(source)
        gate = self.gate(types=policy.load(), source=source, sender=sender,
                         reader=lambda cid: dict(contract))
        gate.applications_reader = lambda uid: []
        first = gate.run(self.action(message_type='contract-reminder-1', fields={'First': 'Ada'},
                                     contract=dict(contract)))
        self.assertEqual(first.outcome, 'held', first.reasons)
        self.assertIn('attachmentCount', ' '.join(first.reasons))
        self.assertIn('notice1', consumed)
        self.assertEqual(sender.delivered, [])
        # A valid sender, creation time and exact native notice were consumed.
        # Only the unrelated attachment count was unreadable. The row is then
        # removed upstream; current structured applications are also empty.
        rows.pop()
        return source, contract, gate, sender

    def test_AS01_consumed_signing_notice_with_bad_media_metadata_blocks_later_reminder(self):
        source, contract, gate, sender = self.observed_notice_then_deleted(invite_hours=10)
        gate.now = lambda: NOW + timedelta(hours=6)
        result = gate.run(self.action(message_type='contract-reminder-2', fields={'First': 'Ada'},
                                      contract=dict(contract)))
        self.assertEqual(sender.delivered, [],
                         f'Signing evidence consumed six hours earlier was lost: {result.outcome}: {result.reasons}')

    def test_AS01_consumed_signing_notice_with_bad_media_metadata_blocks_later_withdrawal(self):
        source, contract, gate, sender = self.observed_notice_then_deleted(invite_hours=35)
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 dict(id='C1', contractorId='U1', status='rejected'))
        result = withdraw.withdraw('C1', lambda cid: dict(contract),
                                   lambda: source.read('chat1', ['U1']), self.j,
                                   'sideshift:U1', NOW + timedelta(hours=6), writer, lambda: [])
        self.assertEqual(writes, [],
                         f'Signing evidence consumed six hours earlier was lost: {result}')
