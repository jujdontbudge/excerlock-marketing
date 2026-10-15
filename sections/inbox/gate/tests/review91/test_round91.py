"""Offline effect-boundary regressions. DA01 and remaining CZ01 assertions fail.

Run: python3 -m unittest discover -s out/tests -t .
Real Flow, Gate, ContactsMCP, SideShiftLive, grant helper and file-backed SQLite.
The fake clocks model macOS sleep: wall time advances, mach_absolute_time does
not. No real sleep, HTTP, entitlement command or production edit is performed.
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

import grant
from gate.tests.review3 import support
from gate.tests.review84.test_round84 import Fixture
from gate.tests.review90 import test_round90 as previous


class Round90Verification(previous.PositiveDncBeforeOtherHold):
    """All thirteen original CZ01 assertions and controls, unchanged."""


class VerifiedRouteRestriction(Fixture):
    def observe_and_move(self, option, withdrawal=False):
        self.setup_system(option=option, distinct=True)
        worker = self.workers['U1']
        original_post = worker.sender._post
        self.first_person = dict(person=dict(id='person1',
            tags=['do-not-contact', {'unreadable': 'other tag'}]), handles=[])
        self.route_reads = []

        def post(body):
            if body['params']['name'] == 'get_person':
                return SimpleNamespace(text=json.dumps(dict(result=dict(content=[
                    dict(type='text', text=json.dumps(self.first_person))]))))
            result = original_post(body)
            if body['params']['name'] == 'get_conversation':
                self.route_reads.append(json.loads(json.loads(result.text)
                    ['result']['content'][0]['text']))
            return result

        worker.sender._post = post
        if withdrawal:
            self.contracts['U1']['status'] = 'pending'
            self.rows['U1'][0]['createdAt'] = (
                support.NOW - timedelta(hours=40)).isoformat()
            writes = []
            worker.job.write_client = SimpleNamespace(request=lambda *a, **kw: writes.append(a))
            first = self.run_job('U1')
            self.assertEqual(writes, [], first)
        else:
            first = worker.gate.run(self.action_for('U1'))
            self.assertEqual(first.outcome, 'held', first)
        # adapted 2026-10-15 (CZ01 fix): the exact do-not-contact tag is now judged before the unreadable sibling
        self.assertIn("person is tagged do-not-contact", str(first))
        self.assertEqual(self.route_reads[-1]['participants'],
            [dict(value_normalized='U1', person_id='person1')])
        self.assertIn('sideshift:U1', self.j.flags('person:person1', 'linked-account'))
        self.assertEqual(self.deliveries, [])
        # The validated route positively linked U1 even though get_person's
        # handles list was empty. No need to infer ownership from an action.
        self.persons['U1'] = 'person3'
        self.handles['person1'] = []
        self.handles['person3'] = ['U1']
        self.clock += timedelta(seconds=20)
        self.elapsed += 20
        self.workers['U1'] = self.worker('U1')
        self.assertIn('do-not-contact', self.first_person['person']['tags'])
        return self.workers['U1']

    def test_CZ01_verified_route_account_must_retain_positive_dnc(self):
        worker = self.observe_and_move('a')
        decision = worker.gate.run(self.action_for('U1'))
        self.assertEqual(self.deliveries, [],
            f'Verified route account lost its positive restriction: {decision}')

    def test_CZ01_verified_route_account_must_hold_draft_mode_withdrawal(self):
        worker = self.observe_and_move('b', withdrawal=True)
        writes = []

        def reject(method, path, **kwargs):
            writes.append((method, path))
            return dict(id='C1', contractorId='U1', status='rejected')

        worker.job.write_client = SimpleNamespace(request=reject)
        worker.job.fetch_contract = lambda cid: dict(self.contracts['U1'])
        report = self.run_job('U1')
        self.assertEqual(writes, [],
            f'Verified route account lost its positive restriction: {report}')


class SleepEvidence(Fixture):
    def advance(self, seconds, asleep):
        self.clock += timedelta(seconds=seconds)
        # mach_absolute_time excludes time asleep. Include a little awake time
        # so neither counterexample relies on an exactly frozen clock.
        self.elapsed += 0.25 if asleep else seconds

    def withdrawal(self, option='a', *, seconds=25, asleep=True):
        self.setup_system(option=option, distinct=True)
        self.contracts['U1']['status'] = 'pending'
        self.rows['U1'][0]['createdAt'] = (
            support.NOW - timedelta(hours=40)).isoformat()
        worker = self.workers['U1']
        self.writes, self.snapshots = [], []
        self.tags = []
        original_post = worker.sender._post

        def post(body):
            response = original_post(body)
            if body['params']['name'] == 'get_person':
                document = json.loads(response.text)
                person = json.loads(document['result']['content'][0]['text'])
                person['person']['tags'] = list(self.tags)
                document['result']['content'][0]['text'] = json.dumps(person)
                return SimpleNamespace(text=json.dumps(document))
            return response

        worker.sender._post = post

        def fetch(cid):
            snapshot = dict(self.contracts['U1'])
            self.snapshots.append((self.clock, snapshot))
            # Contacts was read before sleep. A DNC tag is set remotely during
            # sleep; the worker resumes with the old unrestricted identity.
            self.advance(5, asleep)
            self.tags.append('do-not-contact')
            self.changed_at = self.clock
            self.advance(seconds - 5, asleep)
            return snapshot

        def reject(method, path, **kwargs):
            self.writes.append(dict(method=method, path=path, at=self.clock,
                live_tags=list(self.tags),
                since_change=(self.clock - self.changed_at).total_seconds(),
                age=(self.clock - self.snapshots[-1][0]).total_seconds()))
            return dict(id='C1', contractorId='U1', status='rejected')

        worker.job.fetch_contract = fetch
        worker.job.write_client = SimpleNamespace(request=reject)
        return self.run_job('U1')

    def assert_withdrawal_stops(self, option):
        report = self.withdrawal(option)
        self.assertEqual(self.tags, ['do-not-contact'])
        self.assertEqual((self.clock - support.NOW).total_seconds(), 25)
        self.assertEqual(self.elapsed, 0.5)
        self.assertEqual(self.deliveries, [])
        self.assertEqual(self.writes, [],
            f'25-second-old identity evidence withdrew a restricted creator: '
            f'{self.writes}; {report}')

    def test_DA01_auto_withdrawal_must_count_system_sleep(self):
        self.assert_withdrawal_stops('a')

    def test_DA01_drafts_withdrawal_must_count_system_sleep(self):
        self.assert_withdrawal_stops('b')

    def test_DA01_mixed_withdrawal_must_count_system_sleep(self):
        self.assert_withdrawal_stops('c')

    def test_control_awake_withdrawal_delay_is_already_held(self):
        report = self.withdrawal(asleep=False)
        self.assertEqual(self.writes, [], report)

    def test_control_withdrawal_inside_accepted_window(self):
        report = self.withdrawal(seconds=7)
        self.assertEqual(len(self.writes), 1, report)
        self.assertEqual(self.writes[0]['age'], 7)

    def premium(self, option='a', *, asleep=True):
        self.setup_system(option=option, distinct=True)
        worker = self.workers['U1']
        self.rows['U1'].append(dict(id='email1', senderUserId='U1',
            createdAt=(support.NOW - timedelta(hours=2)).isoformat(),
            content='ada@example.com'))
        self.grants, self.suspensions = [], []

        def trace(sql):
            if sql != 'COMMIT' or self.suspensions:
                return
            claimed = worker.journal.conn.execute(
                "SELECT 1 FROM events WHERE kind='grant-intent'").fetchone()
            if claimed:
                # The real guard passed; the real ownership transaction claimed
                # the email. Suspend at its commit, before grant.py's freshness
                # recheck and before the irreversible entitlement command.
                self.suspensions.append(self.clock)
                self.advance(5, asleep)
                self.contracts['U1']['status'] = 'cancelled'
                self.changed_at = self.clock
                self.advance(20, asleep)

        worker.journal.conn.set_trace_callback(trace)
        self.addCleanup(worker.journal.conn.set_trace_callback, None)

        def runner(argv, **kwargs):
            verb, email = argv[1:3]
            if verb == 'grant':
                self.grants.append(dict(email=email, at=self.clock,
                    live_status=self.contracts['U1']['status'],
                    since_change=(self.clock - self.changed_at).total_seconds(),
                    evidence_age=(self.clock - self.suspensions[0]).total_seconds()))
            return SimpleNamespace(returncode=0,
                stdout=f'{"NONE" if verb == "check" else "GRANTED"}: {email}',
                stderr='')

        worker.gate.granter = lambda a: grant.grant(worker.journal,
            a.creator_key, a.fields['email'], 'offline review', runner=runner)
        return worker.gate.run(replace(self.action_for('U1', 'app-access'),
                                      fields={'email': 'ada@example.com'}))

    def test_DA01_premium_commit_freshness_must_count_system_sleep(self):
        decision = self.premium()
        self.assertEqual(len(self.suspensions), 1)
        self.assertEqual(self.contracts['U1']['status'], 'cancelled')
        self.assertEqual(self.elapsed, 0.5)
        self.assertEqual(self.deliveries, [], decision)
        self.assertEqual(self.grants, [],
            f'Cancelled creator received Premium on 25-second-old authorization: '
            f'{self.grants}; {decision}')

    def test_control_awake_premium_commit_delay_is_already_held(self):
        decision = self.premium(asleep=False)
        self.assertEqual(len(self.suspensions), 1)
        self.assertEqual(self.grants, [], decision)
        self.assertEqual(self.deliveries, [], decision)

    def test_control_drafts_do_not_reach_premium_commit(self):
        decision = self.premium(option='b')
        self.assertEqual(decision.outcome, 'draft', decision)
        self.assertEqual((self.grants, self.suspensions, self.deliveries), ([], [], []))

    def test_control_mixed_does_not_reach_premium_commit(self):
        decision = self.premium(option='c')
        self.assertEqual(decision.outcome, 'draft', decision)
        self.assertEqual((self.grants, self.suspensions, self.deliveries), ([], [], []))
