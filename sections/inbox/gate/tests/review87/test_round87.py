"""Round-87 safety assertions; CW01 intentionally fails against this snapshot.

Real Flow, production contacts_routes, ContactsMCP parser/preflight, SideShiftLive
and file-backed SQLite. Only transport responses and clocks are fake. No network.
Run: python3 -m unittest discover -s out/tests -t .
"""
import json
from datetime import timedelta
from types import SimpleNamespace

from gate.tests.review84.test_round84 import Fixture
from gate.tests.review3 import support


class WithdrawalIdentityFreshness(Fixture):
    def configure(self, option='a', *, delay=25, change='link', writer=True,
                  slow_source='contacts', distinct=True):
        self.setup_system(option=option, distinct=distinct)
        self.contracts['U1']['status'] = 'pending'
        self.rows['U1'][0]['createdAt'] = (
            support.NOW - timedelta(hours=40)).isoformat()
        self.writes, self.identity_reads = [], []
        self.tags, self.changed_at = [], None
        worker = self.workers['U1']
        original_post = worker.sender._post

        def advance(seconds):
            self.elapsed += seconds
            self.clock += timedelta(seconds=seconds)

        def post(body):
            tool = body['params']['name']
            if tool == 'list_conversations':
                result = [dict(id='route1', channel='sideshift',
                               external_id='sideshift:chat1')]
                return SimpleNamespace(text=json.dumps(dict(result=dict(content=[
                    dict(type='text', text=json.dumps(result))]))))
            response = original_post(body)
            if tool == 'get_person':
                # The server has read the person at this time. Its serialized
                # response remains in flight while remote state changes.
                self.identity_reads.append(self.elapsed)
                document = json.loads(response.text)
                result = json.loads(document['result']['content'][0]['text'])
                result['person']['tags'] = list(self.tags)
                document['result']['content'][0]['text'] = json.dumps(result)
                response = SimpleNamespace(text=json.dumps(document))
                if delay and slow_source == 'contacts' and len(self.identity_reads) == 1:
                    advance(5)
                    if change == 'link':
                        self.handles['person1'] = ['U1', 'U2']
                    elif change == 'dnc':
                        self.tags = ['do-not-contact']
                    self.changed_at = self.elapsed
                    advance(delay - 5)
            return response

        worker.sender._post = post
        worker.job.routes = support.flow.contacts_routes(worker.sender)

        def fetch(cid):
            if slow_source == 'sideshift':
                advance(delay)
            return dict(self.contracts['U1'])

        worker.job.fetch_contract = fetch

        def request(method, path, **kwargs):
            self.writes.append(dict(method=method, path=path, at=self.elapsed,
                handles=list(self.handles['person1']), tags=list(self.tags),
                known_accounts=sorted(self.j.component_accounts('sideshift:U1')),
                identity_age=self.elapsed - self.identity_reads[-1]))
            return dict(id='C1', contractorId='U1', status='rejected')

        worker.job.write_client = SimpleNamespace(request=request) if writer else None
        self.j.link_person('person1', 'sideshift:U1')
        return worker

    def assert_stale_identity_holds(self, option='a', change='link'):
        self.configure(option, change=change)
        report = self.run_job('U1')
        self.assertEqual(self.identity_reads[0], 0)
        self.assertEqual(self.changed_at, 5)
        self.assertEqual(self.elapsed, 25)
        self.assertEqual(self.deliveries, [], report)
        if change == 'link':
            self.assertEqual(self.handles['person1'], ['U1', 'U2'])
        self.assertEqual(self.writes, [],
            f'Identity read at t=0; remote {change} at t=5; response at t=25. '
            f'Final SideShift reads take zero seconds. {report}; POSTs={self.writes}')

    def test_CW01_auto_must_bound_identity_evidence_age(self):
        self.assert_stale_identity_holds('a')

    def test_CW01_drafts_must_bound_identity_evidence_age(self):
        self.assert_stale_identity_holds('b')

    def test_CW01_mixed_must_bound_identity_evidence_age(self):
        self.assert_stale_identity_holds('c')

    def test_CW01_remote_restriction_must_not_age_outside_window(self):
        self.assert_stale_identity_holds(change='dnc')

    def test_control_fast_single_account_still_withdraws(self):
        self.configure(delay=0)
        report = self.run_job('U1')
        self.assertEqual(len(self.writes), 1, report)
        self.assertEqual(self.writes[0]['identity_age'], 0)

    def test_control_gap_inside_accepted_window_is_not_reported(self):
        self.configure(delay=7)
        report = self.run_job('U1')
        self.assertEqual(len(self.writes), 1, report)
        self.assertEqual(self.writes[0]['identity_age'], 7)

    def test_control_slow_sideshift_reads_are_already_held(self):
        self.configure(delay=25, slow_source='sideshift')
        report = self.run_job('U1')
        self.assertEqual(self.elapsed, 25)
        self.assertEqual(self.writes, [], report)

    def test_control_missing_writer_contains_stale_identity(self):
        self.configure(writer=False)
        report = self.run_job('U1')
        self.assertEqual(self.writes, [], report)

    def test_control_stable_multiple_accounts_are_discovered_and_held(self):
        self.configure(delay=0, distinct=False)
        report = self.run_job('U1')
        self.assertEqual(self.writes, [], report)
        self.assertIn('other linked SideShift accounts', str(report))
        self.assertEqual(self.j.component_accounts('sideshift:U1'),
                         {'sideshift:U1', 'sideshift:U2'})

    def test_control_missing_sender_holds_withdrawal(self):
        worker = self.configure(delay=0)
        worker.gate.sender = None
        report = self.run_job('U1')
        self.assertEqual(self.writes, [], report)
        self.assertIn('identity could not be checked', str(report))

    def test_control_current_contacts_restriction_holds_withdrawal(self):
        self.configure(delay=0)
        self.tags = ['do-not-contact']
        report = self.run_job('U1')
        self.assertEqual(self.writes, [], report)
        self.assertIn('tagged do-not-contact', str(report))

    def test_control_unreadable_contacts_holds_withdrawal(self):
        worker = self.configure(delay=0)
        original_post = worker.sender._post

        def post(body):
            if body['params']['name'] == 'get_person':
                raise RuntimeError('offline unreadable person')
            return original_post(body)

        worker.sender._post = post
        report = self.run_job('U1')
        self.assertEqual(self.writes, [], report)
        self.assertIn('could not verify the route', str(report))
