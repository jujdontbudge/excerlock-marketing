"""Offline safety assertions against the unchanged reviewed source.

Run: python3 -m unittest discover -s out/tests -t .
Real collectors, Gate, Flow, SideShiftLive, ContactsMCP boundary and SQLite;
only service responses and the review verdict are fakes.
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from gate.tests.review21 import test_round21 as fixtures
from gate.tests.review4.support import NOW, flow, policy, propose


class ApplicationFieldTypes(fixtures.ReviewCase):
    def row(self, **changes):
        return dict(id='request1', programId=flow.CAMPAIGN,
                    creator={'id': 'U1'}, isJoinRequest=False, status='pending',
                    requestedAt=(NOW - timedelta(hours=2)).isoformat()) | changes

    def assert_reminder_held(self, row):
        source = fixtures.clean_source({'U1': fixtures.raw_invite(hours=13)})
        client = SimpleNamespace(pages=lambda *a, **kw: [row])
        gate, sender = self.production_gate(source, client, self.contract_for())
        result = self.reminder(gate, self.contract_for())
        self.assertEqual(sender.delivered, [],
                         f'Unreadable application field certified absence: {result.outcome}: {result.reasons}')

    def assert_withdrawal_held(self, row):
        contract = self.contract_for()
        source = fixtures.clean_source({'U1': fixtures.raw_invite(hours=40)})
        contracts = SimpleNamespace(pages=lambda *a, **kw: [dict(contract)],
                                    request=lambda *a, **kw: {'data': dict(contract)})
        gate, sender = self.configured(source, contract)
        gate.types = {k: replace(t, mode='draft') for k, t in policy.load().items()}
        writes = []
        job = flow.Flow(contracts, source, gate, self.j, lambda chat: ('route1', 'person1'),
                        now=lambda: NOW, write_client=self.writer(writes),
                        read_client=SimpleNamespace(pages=lambda *a, **kw: [row]))
        report = job.run()
        self.assertEqual(sender.delivered, [])
        self.assertEqual(writes, [], f'Malformed application enabled all-draft withdrawal: {report}')

    def test_AL01_string_join_flag_cannot_authorize_reminder(self):
        self.assert_reminder_held(self.row(isJoinRequest='false'))

    def test_AL01_string_join_flag_cannot_authorize_draft_flow_withdrawal(self):
        self.assert_withdrawal_held(self.row(isJoinRequest='false'))

    def test_AL01_non_string_owner_cannot_authorize_reminder(self):
        self.assert_reminder_held(self.row(creator={'id': 123}))

    def test_AL01_non_string_owner_cannot_authorize_draft_flow_withdrawal(self):
        self.assert_withdrawal_held(self.row(creator={'id': 123}))


class CachedName(fixtures.ReviewCase):
    def test_AL02_cached_contacts_name_cannot_override_current_sideshift_identity(self):
        contract = self.contract_for()  # contractorName is Ada Example
        source = fixtures.clean_source({'U1': fixtures.raw_invite(hours=13)})
        gate, sender = self.configured(source, contract)
        facts_seen = []

        def review(conv, text, kind, facts):
            facts_seen.append(facts)
            # There is no name in the chat. SideShift's authoritative Ada
            # identity should be passed to the reviewer or enforced before it.
            return 'SEND', 'The invite is pending and no question is open.', []

        gate.reviewer = review
        detail = dict(id='route1', external_id='sideshift:chat1',
                      participants=[dict(value_normalized='U1', person_id='person1',
                                         profile={'display_name': 'Zoe Other'})], messages=[])
        outcome, note = propose.handle(
            dict(id='in1', channel='sideshift', conversation_id='route1', text='Thanks'),
            dict(action='template', message_type='contract-reminder-2'),
            SimpleNamespace(call=lambda *a, **kw: detail), policy.load(),
            [contract], self.j, gate, False)
        self.assertFalse(any('Hi Zoe,' in send['text'] for send in sender.delivered),
                         f'Live contract says Ada, but cached name was sent: {outcome}: {note}; facts={facts_seen}')

    def test_AL02_name_changed_during_long_review_must_be_reconciled_after_live_get(self):
        contract = self.contract_for()
        current = dict(contract)
        source = fixtures.clean_source({'U1': fixtures.raw_invite(hours=13)})
        gate, sender = self.configured(source, contract)
        clock = [1000.0]
        gate.now = lambda: NOW + timedelta(seconds=clock[0] - 1000.0)
        gate.contract_reader = lambda cid: dict(current)

        def review(*args):
            # The proposed name was correct when the review began. A change
            # during two minutes of review is visible on every later live GET.
            current['contractorName'] = 'Zoe Other'
            clock[0] += 120.0
            return 'SEND', 'The proposed reminder addresses Ada correctly.', []

        gate.reviewer = review
        with patch('time.monotonic', side_effect=lambda: clock[0]):
            result = self.reminder(gate, contract)
        self.assertFalse(any('Hi Ada,' in send['text'] for send in sender.delivered),
                         f'Fresh contract says Zoe after 120s, but Ada survived every final check: {result.outcome}: {result.reasons}')
