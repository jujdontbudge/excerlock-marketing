"""Offline required-behavior counterexamples for review 50.

Run: python3 -m unittest discover -s out/tests -t .
Real SideShift reader, JSON-RPC result parser, preflight/send, Gate, Flow,
SQLite journal and grant logic. Only service responses and review verdict are faked.
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate.contacts import ContactsMCP
from gate.model import Action
from gate.tests.review3.support import Case, grant, handles
from gate.tests.review7.test_round7 import CheckedSender
from gate.tests.review35 import test_round35 as fixtures


class Review50(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def set_tags(self, tags):
        class RPCSender(CheckedSender):
            call = ContactsMCP.call

            def _post(inner, body):
                tool, args = body['params']['name'], body['params']['arguments']
                result = (dict(id=args['person_id'], tags=tags) if tool == 'get_person'
                          else super().call(tool, args))
                return SimpleNamespace(text=json.dumps(dict(jsonrpc='2.0', id=1,
                    result=dict(content=[dict(type='text', text=json.dumps(result))]))))

        self.sender = RPCSender(self.source)
        self.g.sender = self.sender

    def test_BL01_unreadable_tag_entries_block_automatic_reminder(self):
        self.setup_flow()
        # A readable list is not readable tag evidence if an entry is opaque.
        # No alternate tag schema is assumed: unknown DNC must hold.
        self.set_tags([None])
        result = self.job.run()
        self.assertEqual(self.sender.delivered, [],
                         f'Unreadable contact tag was treated as clear permission: {result}')

    def premium_attempt(self, drafts=False):
        self.setup_flow()
        self.set_tags([{'name': 'do-not-contact'}])
        self.current['status'] = 'active'
        self.rows.append(dict(id='email', senderUserId='U1', content='ada@example.com',
                              createdAt=(self.clock - timedelta(hours=1)).isoformat()))
        if drafts:
            self.g.types['app-access'] = replace(self.g.types['app-access'], mode='draft')
        self.commands = []
        entitlement = ['NONE']

        def runner(argv, **kw):
            self.commands.append(argv)
            word = entitlement[0]
            if argv[1] == 'grant':
                entitlement[0], word = 'ACTIVE', 'GRANTED'
            return SimpleNamespace(returncode=0, stdout=f'{word}: ada@example.com', stderr='')

        self.g.granter = lambda a: grant.grant(self.j, a.creator_key, a.fields['email'], 'offline review', runner)
        return self.g.run(Action(message_type='app-access', channel='sideshift',
            conversation_id='route1', source_chat_id='chat1', person_id='person1',
            creator_key='sideshift:U1', occurrence='C1', fields={'email': 'ada@example.com'},
            contract=dict(self.current)))

    def test_BL01_unreadable_tag_entries_block_premium_mutation(self):
        result = self.premium_attempt()
        self.assertEqual([c for c in self.commands if c[1] == 'grant'], [],
                         f'Unknown do-not-contact state allowed Premium grant: {result}; {self.commands}')
        self.assertEqual(self.sender.delivered, [])

    def test_options_b_and_c_premium_drafts_contain_BL01(self):
        result = self.premium_attempt(drafts=True)
        self.assertEqual(self.commands, [], result)
        self.assertEqual(self.sender.delivered, [], result)

    def test_option_b_all_message_drafts_contain_BL01_reminder(self):
        self.setup_flow()
        self.set_tags([None])
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        result = self.job.run()
        self.assertEqual(self.sender.delivered, [], result)

    def test_BL02_chat_notice_cannot_drop_unsupported_requested_platform(self):
        self.setup_flow()
        self.current['status'] = 'active'
        self.rows.append(dict(id='notice', senderUserId='U1',
            createdAt=(self.clock - timedelta(hours=1)).isoformat(),
            content='📨 Requested 3 handles: @ada.walks (tiktok), @ada.walks (instagram), '
                    '@ada_ugc (youtube) for this contract.'))
        self.job.fetchers = {p: (lambda h, p=p: handles.Profile(p, h, True,
            self.clock - timedelta(hours=2) if p == 'tiktok' else None, 0, 0))
            for p in ('tiktok', 'instagram')}
        # Structured requests are empty; Flow uses its documented chat fallback.
        self.job.run()
        verdicts = [json.loads(e['data']) for e in self.j.events('sideshift:U1')
                    if e['kind'] == 'handle-check']
        self.assertEqual(len(verdicts), 1)
        self.assertNotEqual(verdicts[0]['verdict'], 'pass',
                            f'Third account disappeared before the coverage guard: {verdicts[0]}')
