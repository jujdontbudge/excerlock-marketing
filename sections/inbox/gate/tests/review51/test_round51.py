"""Offline required-behavior counterexamples; production code is unchanged.

Run: python3 -m unittest discover -s out/tests -t .
The real JSON-RPC parser, preflight, send boundary, live reader, Gate, Flow,
journal and grant run against fake service responses. No network or real grant.
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate.tests.review3.support import Case, grant, handles
from gate.contacts import ContactsMCP
from gate.model import Action
from gate.tests.review7.test_round7 import CheckedSender
from gate.tests.review35 import test_round35 as fixtures


class Review51(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def unreadable_route(self):
        self.setup_flow()
        self.route_reads = []

        class RPCSender(CheckedSender):
            call = ContactsMCP.call

            def _post(inner, body):
                tool, args = body['params']['name'], body['params']['arguments']
                result = super().call(tool, args)
                if tool == 'get_conversation':
                    # Preserve the known creator; another route entry is unreadable.
                    # This cannot prove there is exactly one participant.
                    result['participants'].append(None)
                    self.route_reads.append(result)
                return SimpleNamespace(text=json.dumps(dict(jsonrpc='2.0', id=1,
                    result=dict(content=[dict(type='text', text=json.dumps(result))]))))

        self.sender = RPCSender(self.source)
        self.g.sender = self.sender

    def test_BM01_unreadable_route_participant_blocks_reminder(self):
        self.unreadable_route()
        result = self.job.run()
        self.assertTrue(self.route_reads)
        self.assertEqual(self.sender.delivered, [],
                         f'Unproven one-to-one route authorized a reminder: {result}')

    def premium(self, drafts=False):
        self.unreadable_route()
        self.current['status'] = 'active'
        self.rows.append(dict(id='email', senderUserId='U1', content='ada@example.com',
                              createdAt=(self.clock - timedelta(hours=1)).isoformat()))
        if drafts:
            self.g.types['app-access'] = replace(self.g.types['app-access'], mode='draft')
        self.commands = []
        active = [False]

        def runner(argv, **kw):
            self.commands.append(argv)
            word = 'ACTIVE' if active[0] else 'NONE'
            if argv[1] == 'grant':
                active[0], word = True, 'GRANTED'
            return SimpleNamespace(returncode=0, stdout=f'{word}: ada@example.com', stderr='')

        self.g.granter = lambda a: grant.grant(self.j, a.creator_key, a.fields['email'], 'offline review', runner)
        return self.g.run(Action(message_type='app-access', channel='sideshift',
            conversation_id='route1', source_chat_id='chat1', person_id='person1',
            creator_key='sideshift:U1', occurrence='C1', fields={'email': 'ada@example.com'},
            contract=dict(self.current)))

    def test_BM01_unreadable_route_participant_blocks_premium_grant(self):
        result = self.premium()
        self.assertEqual([c for c in self.commands if c[1] == 'grant'], [],
                         f'Unproven route authorized Premium mutation: {result}; {self.commands}')
        self.assertEqual(self.sender.delivered, [])

    def test_option_b_drafts_contain_reminder(self):
        self.unreadable_route()
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        result = self.job.run()
        self.assertEqual(self.sender.delivered, [], result)

    def test_options_b_and_c_premium_drafts_contain_grant(self):
        result = self.premium(drafts=True)
        self.assertEqual(self.commands, [], result)
        self.assertEqual(self.sender.delivered, [], result)

    def mismatched_profile(self, platform):
        self.setup_flow()
        self.current['status'] = 'active'
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.rows.append(dict(id='notice', senderUserId='U1',
            createdAt=(self.clock - timedelta(hours=1)).isoformat(),
            content='📨 Requested 2 handles: @ada.walks (tiktok), @ada.walks (instagram) for this contract.'))
        returned = 'different_ugc'  # independently identified by the response, not the requested URL
        self.fetched = []

        def get(url, **kw):
            self.fetched.append(url)
            if 'tiktok.com' in url:
                data = {'__DEFAULT_SCOPE__': {'webapp.user-detail': {'userInfo': {
                    'user': {'uniqueId': returned if platform == 'tiktok' else 'ada.walks',
                             'createTime': int((self.clock - timedelta(hours=2)).timestamp())},
                    'stats': {'videoCount': 0, 'followerCount': 0}}}}}
                return SimpleNamespace(text='<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">'
                                       + json.dumps(data) + '</script>')
            user = {'username': returned if platform == 'instagram' else 'ada.walks',
                    'edge_owner_to_timeline_media': {'count': 0}, 'edge_followed_by': {'count': 0}}
            return SimpleNamespace(json=lambda: {'data': {'user': user}})

        self.job.fetchers = {'tiktok': lambda h: handles.fetch_tiktok(h, get=get),
                             'instagram': lambda h: handles.fetch_instagram(h, get=get)}
        self.job.run()
        verdicts = [json.loads(e['data']) for e in self.j.events('sideshift:U1') if e['kind'] == 'handle-check']
        self.assertEqual(len(self.fetched), 2)
        self.assertEqual(len(verdicts), 1)
        self.assertNotEqual(verdicts[0]['verdict'], 'pass',
            f'{platform} response identifies @{returned}, but a permanent pass is stored for @ada.walks: {verdicts}')

    def test_BM02_tiktok_response_for_another_handle_cannot_pass(self):
        self.mismatched_profile('tiktok')

    def test_BM02_instagram_response_for_another_handle_cannot_pass(self):
        self.mismatched_profile('instagram')
