"""Run all nine original BP01 regressions plus current-evidence controls."""
from gate.tests.review54 import test_round54 as original


class Round54Verification(original.Round54):
    def test_current_chat_conflict_blocks_even_when_contract_name_matches_cached_name(self):
        # Both the listing and every detail GET say Ada. The chat says Beatrice.
        # Every available name must match; the contract cannot override the chat.
        result = self.reply(cached_name='Ada Example', live_name='Beatrice Example', has_contract=True)
        self.assertEqual(self.sender.delivered, [], result)

    def test_live_name_is_in_the_reviewers_verified_facts(self):
        result = self.reply(cached_name='Ada Example')
        self.assertEqual(result[0], 'done', result)
        self.assertEqual(self.review_inputs[0]['verified_facts']['name_on_her_sideshift_chat'], 'Ada Example')

    def test_omitted_current_contract_name_cannot_inherit_the_old_name(self):
        self.setup_flow()
        action = self.action(contract=self.contract(contractorName='Old Example'))
        self.g.contract_reader = lambda cid: {'id': 'C1', 'contractorId': 'U1', 'status': 'pending'}
        fresh, errors = self.g._fresh_contract(action)
        self.assertEqual(errors, [])
        self.assertIsNone(fresh['contractorName'])
