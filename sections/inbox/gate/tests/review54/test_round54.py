"""Required-behavior tests. Real proposal, live reader, gate, journal and transport.
Only remote records and the review verdict are fakes. No network or production edits.
Run: python3 -m unittest discover -s out/tests -t .
"""
import json
from dataclasses import replace
from datetime import timedelta

from gate.review import payload
from gate.tests.review3.support import Case, propose
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review7.test_round7 import CheckedSender


class Round54(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def reply(self, *, cached_name='Beatrice Example', live_name='Ada Example',
              mode='auto', has_contract=False):
        self.setup_flow()
        self.rows = [
            self.raw('outreach', 'Would you be interested in another campaign?',
                     self.clock - timedelta(hours=4)),
            dict(id='capacity', createdAt=(self.clock - timedelta(hours=1)).isoformat(),
                 senderUserId='U1', content='Thank you, I have no room for another campaign.'),
        ]
        source_pages = self.source.client.pages
        self.member_reads = []

        def pages(path, **kwargs):
            if path == '/conversations':
                self.member_reads.append(live_name)
                return [dict(id='chat1', members=[self.source.company_id, 'U1'], participants=[
                    dict(id=self.source.company_id, name='Johan Sardar'),
                    dict(id='U1', name=live_name),
                ])]
            return source_pages(path, **kwargs)

        self.source.client.pages = pages

        class Sender(CheckedSender):
            def call(inner, tool, args):
                result = super().call(tool, args)
                if tool == 'get_conversation':
                    result.update(messages=[], participants=[dict(value_normalized='U1',
                        person_id='person1', profile={'display_name': cached_name})])
                return result

        self.sender = Sender(self.source)
        self.g.sender = self.sender
        allowed = {'contract-reminder-1', 'contract-reminder-2', 'warmup-guide', 'ask-app-email'}
        self.g.types = {key: replace(t, mode=('auto' if key in allowed else 'draft')
                                    if mode == 'selective' else mode)
                        for key, t in self.g.types.items()}
        self.review_inputs = []

        def reviewer(conv, text, message_type, facts):
            # The courtesy response fits the actual live inbound message. There is
            # no name in its text; inspect what the real review is able to verify.
            self.review_inputs.append(json.loads(payload(conv, text, message_type, facts)))
            return 'SEND', 'The courtesy response answers her capacity message.', []

        self.g.reviewer = reviewer
        result = propose.handle(
            dict(id='in-capacity', external_id='sideshift:capacity', channel='sideshift',
                 conversation_id='route1', text=self.rows[1]['content']),
            dict(action='template', message_type='at-capacity'), self.sender, self.g.types,
            [dict(self.current)] if has_contract else [], self.j, self.g, False)
        return result

    def test_BP01_stale_contacts_name_cannot_override_live_name_without_contract(self):
        result = self.reply()
        for sent in self.sender.delivered:
            self.assertTrue(sent['text'].startswith('Hey Ada,'),
                            f'Live participant is Ada; contacts cache rendered another name: {result}; {sent}')

    def test_BP01_missing_live_name_cannot_authorize_cached_personalization(self):
        result = self.reply(live_name=None)
        self.assertEqual(self.sender.delivered, [],
                         f'No current SideShift name was established, but cached name was sent: {result}')

    def test_BP01_control_contract_name_still_blocks_stale_contacts_name(self):
        result = self.reply(has_contract=True)
        self.assertEqual(self.sender.delivered, [], result)

    def test_BP01_control_matching_current_name_can_send(self):
        result = self.reply(cached_name='Ada Example')
        self.assertEqual(result[0], 'done', result)
        self.assertEqual(len(self.sender.delivered), 1)
        self.assertTrue(self.sender.delivered[0]['text'].startswith('Hey Ada,'))

    def test_option_b_drafts_contain_BP01(self):
        result = self.reply(mode='draft')
        self.assertEqual(self.sender.delivered, [], result)
        self.assertEqual(result[0], 'escalated')
        self.assertEqual(self.review_inputs, [])

    def test_option_c_reply_draft_contains_BP01(self):
        result = self.reply(mode='selective')
        self.assertEqual(self.g.types['warmup-guide'].effective_mode, 'auto')
        self.assertEqual(self.g.types['contract-reminder-1'].effective_mode, 'auto')
        self.assertEqual(self.sender.delivered, [], result)
        self.assertEqual(self.g.types['at-capacity'].effective_mode, 'draft')

    def guide(self, *, draft=False, fresh_name=None):
        self.setup_flow()
        self.current.update(status='active', contractorName='Beatrice Example')
        fresh = {**self.current, 'contractorName': fresh_name}
        # The listing is stale; every detail GET is current and consistently
        # lacks a readable name. SideShift's participant is already Ada before
        # this run starts. This is not a change inside the evidence window.
        original_pages = self.source.client.pages

        def pages(path, **kwargs):
            if path == '/conversations':
                return [dict(id='chat1', members=[self.source.company_id, 'U1'], participants=[
                    dict(id='U1', name='Ada Example')])]
            return original_pages(path, **kwargs)

        self.source.client.pages = pages
        self.g.contract_reader = lambda cid: dict(fresh)
        allowed = {'contract-reminder-1', 'contract-reminder-2', 'warmup-guide', 'ask-app-email'}
        self.g.types = {key: replace(t, mode='draft' if draft or key not in allowed else 'auto')
                        for key, t in self.g.types.items()}
        return self.job.run()

    def test_BP01_option_c_guide_cannot_send_stale_name_when_fresh_contract_name_is_unknown(self):
        result = self.guide()
        self.assertEqual(self.g.types['warmup-guide'].effective_mode, 'auto')
        for sent in self.sender.delivered:
            self.assertTrue(sent['text'].startswith('Welcome to ExcerLock, Ada!'),
                            f'Current detail has no name and live participant is Ada; stale list name sent: {result}; {sent}')

    def test_BP01_control_changed_readable_contract_name_blocks_stale_guide(self):
        result = self.guide(fresh_name='Ada Example')
        self.assertEqual(self.sender.delivered, [], result)

    def test_option_b_guide_draft_contains_unknown_name(self):
        result = self.guide(draft=True)
        self.assertEqual(self.sender.delivered, [], result)
