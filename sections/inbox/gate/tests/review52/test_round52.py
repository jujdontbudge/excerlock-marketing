"""Offline required-behavior counterexamples against unchanged production code.

Run: python3 -m unittest discover -s out/tests -t .
Only remote responses, command results, time and the review verdict are faked.
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate.tests.review3.support import Case, flow, grant
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review7.test_round7 import CheckedSender
from gate.contacts import ContactsMCP
from gate.model import Action


class Review52(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def revised_request_then_failed_contract_list(self, *, withdrawal=False, new_id=False):
        self.setup_flow()
        original_types = self.g.types
        self.g.types = {k: replace(t, mode='draft') for k, t in original_types.items()}
        self.current['createdAt'] = (self.clock - timedelta(hours=48)).isoformat()
        if withdrawal:
            self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        row = dict(id='req1', programId=flow.CAMPAIGN, creator={'id': 'U1'},
                   isJoinRequest=False, status='pending', platform='tiktok', handle='ada.walks',
                   requestedAt=(self.clock - timedelta(hours=60)).isoformat())
        applications = [row]
        reads = []

        def application_pages(*a, **kw):
            reads.append([dict(r) for r in applications])
            return [dict(r) for r in applications]

        self.job.read_client = SimpleNamespace(pages=application_pages)
        initial = self.job.run()  # first observation is provably older than this contract
        self.assertEqual(self.sender.delivered, [], initial)
        self.assertNotIn('C1', self.j.flags('sideshift:U1', 'maybe-signed'))
        self.assertTrue(any(e['kind'] == 'request-seen' and
                            json.loads(e['data']).get('requestedAt') == row['requestedAt']
                            for e in self.j.events('sideshift:U1')))

        self.clock += timedelta(minutes=15)
        # The service revises the same record's date. The new date positively
        # places the request after BOTH the contract's creation and its invite.
        row['requestedAt'] = (self.clock - timedelta(hours=1)).isoformat()
        if new_id:
            row['id'] = 'req2'  # control: the same interruption retains a new ID
        normal_contracts = self.job.contracts_client

        def unavailable(*a, **kw):
            raise RuntimeError('offline fake: contract listing unavailable')

        self.job.contracts_client = SimpleNamespace(pages=unavailable)
        with self.assertRaisesRegex(RuntimeError, 'contract listing unavailable'):
            self.job.run()
        self.assertEqual(reads[-1][0]['requestedAt'], row['requestedAt'])
        self.job.contracts_client = normal_contracts

        # The record then vanishes upstream. Fifteen minutes later every
        # remote read is stable. Only the durable request observation can veto.
        applications.clear()
        self.clock += timedelta(minutes=15)
        self.writes = []
        if withdrawal:
            self.job.write_client = SimpleNamespace(request=lambda *a, **kw:
                self.writes.append((a, kw)) or
                dict(id='C1', contractorId='U1', status='rejected'))
        else:
            self.g.types = original_types
        return self.job.run()

    def test_BN01_revised_request_survives_failure_before_contracts_and_blocks_reminder(self):
        report = self.revised_request_then_failed_contract_list()
        self.assertEqual(self.sender.delivered, [],
                         f'Observed post-invite request was forgotten after a failed contract listing: {report}')

    def test_BN01_revised_request_blocks_withdrawal_even_when_all_messages_are_drafts(self):
        report = self.revised_request_then_failed_contract_list(withdrawal=True)
        self.assertEqual(self.sender.delivered, [])
        self.assertEqual(self.writes, [],
                         f'All-draft Flow rejected the invite after forgetting the request revision: {report}')

    def test_BN01_control_new_request_id_survives_the_same_failed_contract_listing(self):
        report = self.revised_request_then_failed_contract_list(withdrawal=True, new_id=True)
        self.assertEqual(self.writes, [], report)
        self.assertTrue(any('linked handles' in line for line in report), report)

    def route_response(self, returned_id='other-route'):
        self.setup_flow()
        self.route_reads = []

        class RPCSender(CheckedSender):
            call = ContactsMCP.call

            def _post(inner, body):
                tool, args = body['params']['name'], body['params']['arguments']
                result = super().call(tool, args)
                if tool == 'get_conversation':
                    result['id'] = returned_id
                    self.route_reads.append((dict(args), dict(result)))
                return SimpleNamespace(text=json.dumps(dict(jsonrpc='2.0', id=1,
                    result=dict(content=[dict(type='text', text=json.dumps(result))]))))

        self.sender = RPCSender(self.source)
        self.g.sender = self.sender

    def test_BN02_response_identifying_another_route_blocks_reminder(self):
        self.route_response()
        report = self.job.run()
        self.assertTrue(self.route_reads)
        self.assertTrue(all(args['conversation_id'] != result['id'] for args, result in self.route_reads))
        self.assertEqual(self.sender.delivered, [],
                         f'Evidence for other-route authorized a send through route1: {report}')

    def premium(self, *, drafts=False):
        self.route_response()
        self.current['status'] = 'active'
        self.rows.append(dict(id='email', senderUserId='U1', content='ada@example.com',
                              createdAt=(self.clock - timedelta(hours=1)).isoformat()))
        if drafts:
            self.g.types['app-access'] = replace(self.g.types['app-access'], mode='draft')
        self.commands, active = [], [False]

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

    def test_BN02_response_identifying_another_route_blocks_premium_mutation(self):
        result = self.premium()
        self.assertEqual([c for c in self.commands if c[1] == 'grant'], [],
                         f'Unverified route1 authorized Premium mutation: {result}; {self.commands}')
        self.assertEqual(self.sender.delivered, [])

    def test_BN02_option_b_reminder_draft_contains_route_defect(self):
        self.route_response()
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        report = self.job.run()
        self.assertEqual(self.sender.delivered, [], report)
        # adapted 2026-10-15 (BN02 fix): the route check now holds before the draft stage; either contains it
        self.assertTrue(any('draft' in line or 'held' in line for line in report), report)

    def test_BN02_options_b_and_c_premium_draft_contains_route_defect(self):
        result = self.premium(drafts=True)
        self.assertIn(result.outcome, ('draft', 'held'))   # adapted 2026-10-15: held earlier by the BN02 fix
        self.assertEqual(self.commands, [])
        self.assertEqual(self.sender.delivered, [])

    def test_BN02_control_matching_route_identity_allows_clean_reminder(self):
        self.route_response(returned_id='route1')
        report = self.job.run()
        self.assertEqual(len(self.sender.delivered), 1, report)
