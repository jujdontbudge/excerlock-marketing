"""Offline regressions: real Gate, Flow, ContactsMCP, SideShiftLive and SQLite.
Run: python3 -m unittest discover -s out/tests -t .
Only remote replies, reviewer and clocks are fake; support forbids HTTP.
"""
import json
from datetime import timedelta
from types import SimpleNamespace

from gate.tests.review84.test_round84 import Fixture
from gate.tests.review3 import support
from gate.tests.review89 import test_round89 as round89


class Round89Verification(round89.RemoteRestrictionMove):
    """Re-run all ten round-89 assertions, including the adapted draft control."""


class PositiveDncBeforeOtherHold(Fixture):
    def configure(self, option, obstruction):
        self.setup_system(option=option, distinct=True)
        self.tags = {'person1': ['do-not-contact'], 'person2': [], 'person3': []}
        if obstruction == 'mixed-tags':
            self.tags['person1'].append({'unreadable': 'other tag'})
        self.obstruction = obstruction
        self.person_reads = []
        self.install_responses(self.workers['U1'])

    def install_responses(self, worker):
        original = worker.sender._post

        def post(body):
            tool = body['params']['name']
            if tool == 'get_person':
                pid = body['params']['arguments']['person_id']
                result = dict(person=dict(id=pid, tags=list(self.tags[pid])), handles=[
                    dict(channel='sideshift', value_normalized=u, person_id=pid)
                    for u in self.handles[pid]])
                self.person_reads.append(result)
                return SimpleNamespace(text=json.dumps(dict(result=dict(content=[
                    dict(type='text', text=json.dumps(result))]))))
            response = original(body)
            if tool == 'get_conversation' and self.obstruction == 'bad-route':
                document = json.loads(response.text)
                result = json.loads(document['result']['content'][0]['text'])
                # A transient incomplete route, while get_person still identifies
                # person1, U1 and the exact positive DNC tag without ambiguity.
                result['participants'] = []
                document['result']['content'][0]['text'] = json.dumps(result)
                return SimpleNamespace(text=json.dumps(document))
            return response
        worker.sender._post = post

    def observe_then_move(self, option, obstruction, withdrawal=False):
        self.configure(option, obstruction)
        worker = self.workers['U1']
        if withdrawal:
            self.contracts['U1']['status'] = 'pending'
            self.rows['U1'][0]['createdAt'] = (support.NOW - timedelta(hours=40)).isoformat()
            writes = []
            worker.job.write_client = SimpleNamespace(request=lambda *a, **kw: writes.append(a))
            report = self.run_job('U1')  # Flow.identity_check, not a synthetic journal injection
            self.assertEqual(writes, [], report)
            self.assertIn('withdraw held', str(report))
        else:
            first = worker.gate.run(self.action_for('U1'))
            self.assertEqual(first.outcome, 'held', first)
        self.assertEqual(self.deliveries, [])
        self.assertTrue(self.person_reads)
        positive = self.person_reads[-1]
        self.assertEqual(positive['person']['id'], 'person1')
        self.assertIn('do-not-contact', positive['person']['tags'])
        self.assertEqual(positive['handles'][0]['value_normalized'], 'U1')
        # Leave the restriction on person1. Repair only the unrelated route/tag
        # defect and move U1 to person3. No captain releases either DNC source.
        self.persons['U1'] = 'person3'
        self.handles['person1'] = []
        self.handles['person3'] = ['U1']
        self.obstruction = None
        self.elapsed += 20
        self.clock += timedelta(seconds=20)
        self.workers['U1'] = self.worker('U1')  # new SQLite connection, same durable file
        self.install_responses(self.workers['U1'])
        self.assertIn('do-not-contact', self.tags['person1'])
        return self.workers['U1']

    def assert_send_held(self, option, obstruction):
        worker = self.observe_then_move(option, obstruction)
        decision = worker.gate.run(self.action_for('U1'))
        self.assertEqual(self.deliveries, [],
            f'Positive DNC read before {obstruction} was forgotten after restart: {decision}')

    def assert_withdrawal_held(self, option, obstruction):
        worker = self.observe_then_move(option, obstruction, withdrawal=True)
        writes = []
        def reject(method, path, **kwargs):
            writes.append((method, path))
            return dict(id='C1', contractorId='U1', status='rejected')
        worker.job.write_client = SimpleNamespace(request=reject)
        worker.job.fetch_contract = lambda cid: dict(self.contracts['U1'])
        report = self.run_job('U1')
        self.assertEqual(writes, [],
            f'Positive DNC read before {obstruction} was forgotten; real Flow rejected invite: {report}')

    def test_CZ01_auto_mixed_tags_must_retain_positive_dnc(self):
        self.assert_send_held('a', 'mixed-tags')

    def test_CZ01_mixed_mode_mixed_tags_must_retain_positive_dnc(self):
        self.assert_send_held('c', 'mixed-tags')

    def test_CZ01_auto_bad_route_must_retain_positive_dnc(self):
        self.assert_send_held('a', 'bad-route')

    def test_CZ01_mixed_mode_bad_route_must_retain_positive_dnc(self):
        self.assert_send_held('c', 'bad-route')

    def test_CZ01_auto_mixed_tags_must_block_withdrawal(self):
        self.assert_withdrawal_held('a', 'mixed-tags')

    def test_CZ01_drafts_mixed_tags_must_block_withdrawal(self):
        self.assert_withdrawal_held('b', 'mixed-tags')

    def test_CZ01_mixed_mode_mixed_tags_must_block_withdrawal(self):
        self.assert_withdrawal_held('c', 'mixed-tags')

    def test_CZ01_auto_bad_route_must_block_withdrawal(self):
        self.assert_withdrawal_held('a', 'bad-route')

    def test_CZ01_drafts_bad_route_must_block_withdrawal(self):
        self.assert_withdrawal_held('b', 'bad-route')

    def test_CZ01_mixed_mode_bad_route_must_block_withdrawal(self):
        self.assert_withdrawal_held('c', 'bad-route')

    def test_control_drafts_contain_message_after_mixed_tags(self):
        worker = self.observe_then_move('b', 'mixed-tags')
        decision = worker.gate.run(self.action_for('U1'))
        self.assertIn(decision.outcome, ('draft', 'held'), decision)
        self.assertEqual(self.deliveries, [])

    def test_control_drafts_contain_message_after_bad_route(self):
        worker = self.observe_then_move('b', 'bad-route')
        decision = worker.gate.run(self.action_for('U1'))
        self.assertIn(decision.outcome, ('draft', 'held'), decision)
        self.assertEqual(self.deliveries, [])

    def test_control_valid_tag_is_durable_before_move(self):
        self.configure('a', None)
        decision = self.workers['U1'].gate.run(self.action_for('U1'))
        self.assertEqual(decision.outcome, 'held', decision)
        self.assertTrue(self.j.flags('sideshift:U1', 'remote-dnc'))
        self.assertTrue(self.j.restricted('sideshift:U1'))
        self.assertEqual(self.deliveries, [])
