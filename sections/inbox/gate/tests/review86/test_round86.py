"""Offline safety assertions. CV01 tests intentionally fail against this snapshot.

Real Flow, routes adapter, Gate, Contacts preflight/send, SideShiftLive and SQLite;
only transport responses, clocks, review verdicts and Premium subprocesses are fake.
Run: python3 -m unittest discover -s out/tests -t .
"""
import json
import unittest
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate.tests.review84.test_round84 import Fixture
from gate.tests.review3 import support
import grant


class WithdrawalLinkDiscovery(Fixture):
    def run_withdrawal(self, option='a', *, distinct=False, observe_first=False,
                       writer=True):
        self.setup_system(option=option, distinct=distinct)
        worker = self.workers['U1']
        self.contracts['U1']['status'] = 'pending'
        self.rows['U1'][0]['createdAt'] = (
            support.NOW - timedelta(hours=40)).isoformat()
        self.writes, self.contact_reads = [], []
        original_post = worker.sender._post

        def post(body):
            tool = body['params']['name']
            self.contact_reads.append(tool)
            if tool == 'list_conversations':
                result = [dict(id='route1', channel='sideshift',
                               external_id='sideshift:chat1')]
                return SimpleNamespace(text=json.dumps(dict(result=dict(content=[
                    dict(type='text', text=json.dumps(result))]))))
            return original_post(body)

        worker.sender._post = post
        # Use production route discovery: it reads the route's participant and
        # person ID, but never get_person's current handles.
        worker.job.routes = support.flow.contacts_routes(worker.sender)
        worker.job.fetch_contract = lambda cid: dict(self.contracts['U1'])

        def request(method, path, **kwargs):
            self.writes.append((method, path, kwargs))
            return dict(id='C1', contractorId='U1', status='rejected')

        worker.job.write_client = SimpleNamespace(request=request) if writer else None
        # Only U1 was learned in the past. The extra handle is a stable Contacts
        # fact before this job, not a change after its last check.
        self.j.link_person('person1', 'sideshift:U1')
        self.assertEqual(self.j.component_accounts('sideshift:U1'), {'sideshift:U1'})
        if observe_first:
            worker.sender.preflight(self.action_for('U1'))
            self.assertEqual(self.j.component_accounts('sideshift:U1'),
                             {'sideshift:U1', 'sideshift:U2'})
        report = self.run_job('U1')
        self.assertEqual(self.deliveries, [], report)
        return report

    def test_CV01_auto_must_discover_current_link_before_withdrawal(self):
        report = self.run_withdrawal()
        self.assertEqual(self.writes, [], (report, self.contact_reads))

    def test_CV01_all_drafts_must_discover_current_link_before_withdrawal(self):
        report = self.run_withdrawal(option='b')
        self.assertEqual(self.writes, [], (report, self.contact_reads))

    def test_CV01_mixed_must_discover_current_link_before_withdrawal(self):
        report = self.run_withdrawal(option='c')
        self.assertEqual(self.writes, [], (report, self.contact_reads))

    def test_CV01_repeated_jobs_must_not_leave_current_links_unread_forever(self):
        report = self.run_withdrawal(writer=False)
        self.assertEqual(self.writes, [], report)
        self.clock += timedelta(hours=3)
        self.elapsed += 3 * 3600
        worker = self.workers['U1']

        def request(*args, **kwargs):
            self.writes.append(args)
            return dict(id='C1', contractorId='U1', status='rejected')

        worker.job.write_client = SimpleNamespace(request=request)
        report = self.run_job('U1')
        self.assertEqual(self.writes, [], (report, self.contact_reads))

    def test_control_already_journaled_links_hold_withdrawal(self):
        report = self.run_withdrawal(observe_first=True)
        self.assertEqual(self.writes, [], report)
        self.assertIn('other linked SideShift accounts', str(report))

    def test_control_true_single_account_still_withdraws(self):
        report = self.run_withdrawal(distinct=True)
        self.assertEqual(len(self.writes), 1, report)

    def test_control_missing_writer_contains_withdrawal(self):
        report = self.run_withdrawal(writer=False)
        self.assertEqual(self.writes, [], report)


class MidRunHold(Fixture):
    def connect(self):
        self.handles['person1'] = ['U1', 'U2']
        self.workers['U1'].sender.preflight(self.action_for('U1'))
        self.assertEqual(self.j.component_accounts('sideshift:U1'),
                         {'sideshift:U1', 'sideshift:U2'})

    def test_control_link_learned_during_review_holds_actual_send(self):
        self.setup_system(distinct=True)
        worker = self.workers['U1']

        def review(*args):
            self.connect()
            self.clock += timedelta(seconds=20)
            self.elapsed += 20
            return 'SEND', 'offline review', []

        worker.gate.reviewer = review
        result = worker.gate.run(self.action_for('U1'))
        self.assertEqual(self.deliveries, [], result)
        self.assertIn('other linked SideShift accounts', str(result.reasons))

    def test_control_link_learned_during_entitlement_check_holds_actual_grant(self):
        self.setup_system(distinct=True)
        self.rows['U1'].append(dict(id='email1', senderUserId='U1',
            createdAt=(support.NOW - timedelta(hours=2)).isoformat(),
            content='ada@example.com'))
        grants = []

        def runner(argv, **kwargs):
            verb, email = argv[1:3]
            if verb == 'check':
                self.connect()
                return SimpleNamespace(returncode=0, stdout='NONE: ' + email, stderr='')
            grants.append(email)
            return SimpleNamespace(returncode=0, stdout='GRANTED: ' + email, stderr='')

        worker = self.workers['U1']
        worker.gate.granter = lambda a: grant.grant(worker.journal, a.creator_key,
            a.fields['email'], 'offline review', runner=runner)
        result = worker.gate.run(replace(self.action_for('U1', 'app-access'),
                                        fields={'email': 'ada@example.com'}))
        self.assertEqual(grants, [], result)
        self.assertEqual(self.deliveries, [], result)
        self.assertIn('other linked SideShift accounts', str(result.reasons))

    def test_control_single_account_grant_in_flight_cannot_be_joined_by_second_grant(self):
        # The old CU03 reproduction now stops before its first grant because it
        # starts with two accounts. Start with two separate SINGLE accounts to
        # exercise the actual merge while the first request is in flight.
        self.setup_system(distinct=True)
        grants, second = [], []
        for uid in ('U1', 'U2'):
            email = uid.lower() + '@example.com'
            self.rows[uid].append(dict(id='email-' + uid, senderUserId=uid,
                createdAt=(support.NOW - timedelta(hours=2)).isoformat(), content=email))
            worker = self.workers[uid]

            def runner(argv, uid=uid, **kwargs):
                verb, email = argv[1:3]
                if verb == 'check':
                    return SimpleNamespace(returncode=0, stdout='NONE: ' + email, stderr='')
                grants.append(email)
                if uid == 'U2':
                    self.assertIn(('sideshift:U2', 'grant-intent'),
                                  self.j.premium_owners(email))
                    self.connect()
                    self.clock += timedelta(seconds=20)
                    self.elapsed += 20
                    second.append(self.workers['U1'].gate.run(replace(
                        self.action_for('U1', 'app-access'), fields={'email': 'u1@example.com'})))
                return SimpleNamespace(returncode=0, stdout='GRANTED: ' + email, stderr='')

            worker.gate.granter = lambda a, w=worker, r=runner: grant.grant(
                w.journal, a.creator_key, a.fields['email'], 'offline review', runner=r)

        first = self.workers['U2'].gate.run(replace(self.action_for('U2', 'app-access'),
                                                 fields={'email': 'u2@example.com'}))
        self.assertEqual(grants, ['u2@example.com'], (first, second))
        self.assertEqual(len(second), 1)
        self.assertIn('other linked SideShift accounts', str(second[0].reasons))
        self.assertEqual(self.deliveries, [], (first, second))

    def test_control_link_learned_during_withdrawal_checks_holds(self):
        self.setup_system(distinct=True)
        self.contracts['U1']['status'] = 'pending'
        self.rows['U1'][0]['createdAt'] = (
            support.NOW - timedelta(hours=40)).isoformat()
        worker = self.workers['U1']
        writes = []

        def fetch(cid):
            self.connect()
            return dict(self.contracts['U1'])

        worker.job.fetch_contract = fetch
        worker.job.write_client = SimpleNamespace(request=lambda *a, **kw:
            writes.append(a) or dict(id='C1', contractorId='U1', status='rejected'))
        report = self.run_job('U1')
        self.assertEqual(writes, [], report)
        self.assertIn('other linked SideShift accounts', str(report))


if __name__ == '__main__':
    unittest.main()
