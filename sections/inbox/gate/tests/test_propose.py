"""The inbox runner trusts nothing the model says: proposals are validated before the gate ever sees them."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import propose as P  # noqa: E402
from gate import policy  # noqa: E402

TYPES = policy.load()
INBOUND = {'id': 'm1', 'channel': 'sideshift', 'conversation_id': 'c1'}
CONV = {'id': 'c1', 'participants': [{'person_id': 'p1', 'value_normalized': 'U1', 'profile': {'display_name': 'Kamila Rueda'}}]}


class Parse(unittest.TestCase):
    def test_garbage_escalates_everything(self):
        for out in ('', 'I think we should send the brief', '{"action": "template"}', '[1, 2',
                    'blah [{"message_id": "m1", "action": "escalate"}] tail'):
            r = P.parse_proposals(out, {'m1', 'm2'})
            self.assertEqual({v['action'] for v in r.values()}, {'escalate'})

    def test_unknown_actions_ids_and_duplicates_escalate(self):
        out = '[{"message_id": "m1", "action": "send_anything"}, {"message_id": "zz", "action": "template"},' \
              ' {"message_id": "m2", "action": "template", "message_type": "at-capacity"},' \
              ' {"message_id": "m2", "action": "ignore", "reason": "x"}]'
        r = P.parse_proposals(out, {'m1', 'm2'})
        self.assertEqual((r['m1']['action'], r['m2']['action']), ('escalate', 'escalate'))
        self.assertNotIn('zz', r)

    def test_one_clean_proposal_per_message_is_kept(self):
        r = P.parse_proposals('[{"message_id": "m1", "action": "template", "message_type": "at-capacity"}]', {'m1'})
        self.assertEqual(r['m1']['action'], 'template')


class Build(unittest.TestCase):
    def build(self, proposal, inbound=INBOUND, chat='chat1', her=('hi',)):
        return P.build_action(proposal, inbound, CONV, TYPES, chat, 'Kamila', list(her))

    def test_valid_template(self):
        a, why = self.build({'message_type': 'at-capacity'})
        self.assertIsNone(why)
        self.assertEqual((a.fields, a.creator_key, a.occurrence), ({'First': 'Kamila'}, 'sideshift:U1', 'm1'))

    def test_model_cannot_choose_the_name(self):
        a, _ = self.build({'message_type': 'at-capacity', 'fields': {'First': 'Emma'}})
        self.assertEqual(a.fields['First'], 'Kamila')

    def test_unknown_type_and_other_channels_rejected(self):
        self.assertIsNone(self.build({'message_type': 'promise-500-advance'})[0])
        self.assertIsNone(self.build({'message_type': 'at-capacity'}, inbound={**INBOUND, 'channel': 'email'})[0])
        self.assertIsNone(self.build({'message_type': 'at-capacity'}, chat=None)[0])

    def test_email_must_be_in_her_own_words(self):
        ok, _ = self.build({'message_type': 'app-access', 'fields': {'email': 'Kamila.R@gmail.com'}}, her=('use kamila.r@gmail.com pls',))
        self.assertEqual(ok.fields['email'], 'kamila.r@gmail.com')
        for email in ('kamila.r@gmail.co', 'attacker@evil.com', 'not an email', ''):
            self.assertIsNone(self.build({'message_type': 'app-access', 'fields': {'email': email}}, her=('use kamila.r@gmail.com',))[0])


if __name__ == '__main__':
    unittest.main()


class Prepare(unittest.TestCase):
    """Granting moved into the gate (review N02); the runner only attaches the contract and refuses inactive ones."""
    def action(self, mt='app-access'):
        a, _ = P.build_action({'message_type': mt, 'fields': {'email': 'kamila@gmail.com'}}, INBOUND, CONV, TYPES, 'chat1',
                              'Kamila', ['kamila@gmail.com'])
        return a

    def test_app_access_needs_exactly_one_active_contract(self):
        active = [{'id': 'C1', 'contractorId': 'U1', 'status': 'active'}]
        self.assertIsNone(P.prepare(self.action(), active, None, 'Kamila')[1])
        for contracts in ([{'id': 'C1', 'contractorId': 'U1', 'status': 'pending'}], [],
                          active + [{'id': 'C2', 'contractorId': 'U1', 'status': 'active'}]):
            self.assertIsNone(P.prepare(self.action(), contracts, None, 'Kamila')[0])

    def test_claims_only_cover_what_was_claimed(self):
        self.assertEqual(P.claimed_ids({}, ['a']), (set(), None))
        self.assertEqual(P.claimed_ids({'claim_token': 't'}, ['a', 'b']), ({'a', 'b'}, 't'))
        self.assertEqual(P.claimed_ids({'claim_token': 't', 'message_ids': ['b', 'zz']}, ['a', 'b']), ({'b'}, 't'))


if __name__ == '__main__':
    unittest.main()
