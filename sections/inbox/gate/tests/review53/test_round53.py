"""Offline counterexamples: required behavior, unchanged production modules.
Run: python3 -m unittest discover -s out/tests -t .
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.tests.review3.support import Case, propose
from gate.contacts import ContactsMCP
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review7.test_round7 import CheckedSender


class Review53(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def notice_revision(self, *, withdrawal=False, new_id=False):
        self.setup_flow()
        self.current['createdAt'] = (self.clock - timedelta(hours=48)).isoformat()
        if withdrawal:
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
            self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        notice = dict(id='notice1', senderUserId='U1',
                      content='📨 Requested handle @ada.walks (tiktok) for this contract.',
                      createdAt=(self.clock - timedelta(hours=60)).isoformat())
        self.rows.append(notice)
        # A read-only record viewer uses the same production notice hook.
        self.source.read('chat1', ['U1'])
        self.assertFalse(checks.recorded_signing(self.current, self.j.events('sideshift:U1')))
        notice['createdAt'] = (self.clock - timedelta(hours=30 if withdrawal else 1)).isoformat()
        if new_id:
            notice['id'] = 'notice2'
        observed = self.source.read('chat1', ['U1'])
        self.assertTrue(checks.signing_seen(observed, self.current))
        self.assertTrue(any(e['kind'] == 'msg-seen' and
                            json.loads(e['data']).get('at') == notice['createdAt']
                            for e in self.j.events('sideshift:U1')))
        # Native redaction retains id, sender and the corrected creation time.
        # No contract-processing worker ran between these read-only observations.
        notice.update(content='', isEdited=True)
        self.clock += timedelta(minutes=15)
        self.writes = []
        if withdrawal:
            self.job.write_client = SimpleNamespace(request=lambda *a, **kw:
                self.writes.append((a, kw)) or
                dict(id='C1', contractorId='U1', status='rejected'))
        return self.job.run()

    def test_BO01_revised_notice_date_survives_redaction_before_reminder(self):
        report = self.notice_revision()
        self.assertEqual(self.sender.delivered, [],
                         f'Observed post-invite signing notice lost its veto after redaction: {report}')

    def test_BO01_revised_notice_date_survives_redaction_before_all_draft_withdrawal(self):
        report = self.notice_revision(withdrawal=True)
        self.assertEqual(self.sender.delivered, [])
        self.assertEqual(self.writes, [],
                         f'All-draft Flow rejected after losing an observed signing notice revision: {report}')

    def test_BO01_control_new_notice_id_preserves_the_same_evidence(self):
        report = self.notice_revision(withdrawal=True, new_id=True)
        self.assertEqual(self.writes, [], report)
        self.assertTrue(any('linked handles' in line for line in report), report)

    def mismatched_proposer_route(self, *, draft=False, matching=False):
        self.setup_flow()
        self.requests = []
        # route-for-other belongs to U9. Its first read incorrectly returns
        # U1's route1 record. All subsequent reads verify route1 correctly.
        requested_route = 'route1' if matching else 'route-for-other'

        class RPCSender(CheckedSender):
            call = ContactsMCP.call

            def _post(inner, body):
                tool, args = body['params']['name'], body['params']['arguments']
                self.requests.append((tool, dict(args)))
                result = super().call(tool, args)
                if tool == 'get_conversation':
                    result.update(id='route1', messages=[], participants=[dict(
                        value_normalized='U1', person_id='person1', profile={'display_name': 'Ada Example'})])
                return SimpleNamespace(text=json.dumps(dict(jsonrpc='2.0', id=1,
                    result=dict(content=[dict(type='text', text=json.dumps(result))]))))

        self.sender = RPCSender(self.source)
        self.g.sender = self.sender
        if draft:
            self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        return propose.handle(
            dict(id='in-U9', external_id='sideshift:question-U9', channel='sideshift',
                 conversation_id=requested_route, text='I have no room for another campaign.',
                 person={'name': 'Ada Example' if matching else 'Other Creator'}),
            dict(action='template', message_type='at-capacity'),
            self.sender, self.g.types, [dict(self.current)], self.j, self.g, False)

    def test_BO02_proposer_cannot_replace_inbound_route_with_returned_route(self):
        outcome = self.mismatched_proposer_route()
        self.assertEqual(self.requests[0], ('get_conversation', dict(conversation_id='route-for-other', limit=200)))
        self.assertEqual(self.sender.delivered, [],
                         f'U9 proposal was sent to U1 after returned id replaced the claimed route: {outcome}')

    def test_BO02_draft_mode_contains_wrong_recipient_send(self):
        outcome = self.mismatched_proposer_route(draft=True)
        self.assertEqual(self.sender.delivered, [], outcome)
        self.assertEqual(outcome[0], 'escalated')

    def test_BO02_control_matching_inbound_route_allows_template(self):
        outcome = self.mismatched_proposer_route(matching=True)
        self.assertEqual(len(self.sender.delivered), 1, outcome)
        self.assertEqual(self.sender.delivered[0]['conversation_id'], 'route1')
