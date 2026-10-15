"""Offline assertions at production Flow / Gate / ContactsMCP boundaries.
Run: python3 -m unittest discover -s out/tests -t .
"""
import json
from datetime import timedelta
from types import SimpleNamespace

from gate.tests.review84.test_round84 import Fixture
from gate.tests.review3 import support


class RemoteRestrictionMove(Fixture):
    def configure(self, option='a', tagged=True):
        self.setup_system(option=option, distinct=True)
        self.tags = {'person1': ['do-not-contact'] if tagged else [], 'person2': [], 'person3': []}
        worker = self.workers['U1']
        original_post = worker.sender._post

        def post(body):
            tool = body['params']['name']
            if tool == 'get_person':
                pid = body['params']['arguments']['person_id']
                result = dict(person=dict(id=pid, tags=list(self.tags[pid])), handles=[
                    dict(channel='sideshift', value_normalized=u, person_id=pid)
                    for u in self.handles[pid]])
                return SimpleNamespace(text=json.dumps(dict(result=dict(content=[
                    dict(type='text', text=json.dumps(result))]))))
            return original_post(body)

        worker.sender._post = post
        return worker, post

    def observe_then_move(self, option='a', tagged=True, withdrawal=False, local_dnc=False):
        worker, post = self.configure(option, tagged=tagged)
        if withdrawal:
            self.contracts['U1']['status'] = 'pending'
            self.rows['U1'][0]['createdAt'] = (support.NOW - timedelta(hours=40)).isoformat()
        first = worker.gate.run(self.action_for('U1'))
        if tagged:
            self.assertEqual(first.outcome, 'held', first)
            self.assertIn('tagged do-not-contact', str(first.reasons))
        else:
            self.assertEqual(first.outcome, 'held' if withdrawal else 'sent', first)
        if local_dnc:
            self.j.event('sideshift:U1', 'do-not-contact', 'captain-stop', {'enabled': True})
        # The same SideShift account is re-linked to a new Contacts person.
        # The old person still has its do-not-contact tag; nobody clears it.
        self.persons['U1'] = 'person3'
        self.handles['person1'] = []
        self.handles['person3'] = ['U1']
        self.elapsed += 20
        self.clock += timedelta(seconds=20)
        # New worker/connection, same journal, current remote identity.
        self.workers['U1'] = self.worker('U1')
        current = self.workers['U1']
        base_post = current.sender._post

        def new_post(body):
            if body['params']['name'] == 'get_person':
                return post(body)
            return base_post(body)

        current.sender._post = new_post
        self.assertEqual(self.tags['person1'], ['do-not-contact'] if tagged else [])
        self.assertEqual(self.j.component_accounts('sideshift:U1'), {'sideshift:U1'})
        return current

    def assert_move_holds(self, option):
        self.observe_then_move(option)
        d = self.workers['U1'].gate.run(self.action_for('U1'))
        self.assertEqual(self.deliveries, [],
            f'Previously observed DNC is still on person1; account moved to person3. {d}')

    def test_CY01_auto_must_retain_observed_remote_dnc_after_person_move(self):
        self.assert_move_holds('a')

    def test_CY01_mixed_must_retain_observed_remote_dnc_after_person_move(self):
        self.assert_move_holds('c')

    def test_control_drafts_contain_remote_dnc_move(self):
        self.observe_then_move('b')
        d = self.workers['U1'].gate.run(self.action_for('U1'))
        # adapted 2026-10-15 (CY01 fix): the remembered tag now holds before a draft is even made
        self.assertEqual(d.outcome, 'held', d)
        self.assertEqual(self.deliveries, [])

    def assert_withdrawal_holds(self, option):
        worker = self.observe_then_move(option, withdrawal=True)
        writes = []

        def reject(method, path, **kwargs):
            writes.append((method, path))
            return dict(id='C1', contractorId='U1', status='rejected')

        worker.job.write_client = SimpleNamespace(request=reject)
        worker.job.fetch_contract = lambda cid: dict(self.contracts['U1'])
        report = self.run_job('U1')
        self.assertEqual(writes, [],
            f'Observed person1 DNC was never cleared, but reparented account was withdrawn: {report}')

    def test_CY01_auto_must_not_withdraw_after_remote_dnc_person_move(self):
        self.assert_withdrawal_holds('a')

    def test_CY01_all_drafts_must_not_withdraw_after_remote_dnc_person_move(self):
        self.assert_withdrawal_holds('b')

    def test_CY01_mixed_must_not_withdraw_after_remote_dnc_person_move(self):
        self.assert_withdrawal_holds('c')

    def test_control_current_remote_tag_still_holds_after_restart(self):
        self.configure()
        self.workers['U1'] = self.worker('U1')
        # Configure the remote response on the new worker without a person move.
        worker = self.workers['U1']
        base_post = worker.sender._post

        def post(body):
            response = base_post(body)
            if body['params']['name'] == 'get_person':
                document = json.loads(response.text)
                result = json.loads(document['result']['content'][0]['text'])
                result['person']['tags'] = ['do-not-contact']
                document['result']['content'][0]['text'] = json.dumps(result)
                return SimpleNamespace(text=json.dumps(document))
            return response

        worker.sender._post = post
        d = worker.gate.run(self.action_for('U1'))
        self.assertEqual(d.outcome, 'held', d)
        self.assertEqual(self.deliveries, [])

    def test_control_local_dnc_survives_same_person_move(self):
        self.observe_then_move(local_dnc=True)
        d = self.workers['U1'].gate.run(self.action_for('U1'))
        self.assertEqual(d.outcome, 'held', d)
        self.assertEqual(self.deliveries, [])

    def test_control_untagged_person_move_still_allows_onboarding(self):
        self.observe_then_move(tagged=False)
        # The guide already sent before the move; use the next scheduled type.
        self.clock += timedelta(hours=1)
        self.elapsed += 3600
        d = self.workers['U1'].gate.run(self.action_for('U1', 'ask-app-email'))
        self.assertEqual(d.outcome, 'sent', d)
        self.assertEqual(len(self.deliveries), 2)

    def test_control_no_person_move_remote_dnc_holds_withdrawal(self):
        worker, _ = self.configure('b')
        self.contracts['U1']['status'] = 'pending'
        self.rows['U1'][0]['createdAt'] = (support.NOW - timedelta(hours=40)).isoformat()
        writes = []
        worker.job.write_client = SimpleNamespace(request=lambda *a, **kw: writes.append(a))
        report = self.run_job('U1')
        self.assertEqual(writes, [], report)
        self.assertIn('tagged do-not-contact', str(report))
