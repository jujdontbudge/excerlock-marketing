"""Offline round-11 counterexamples; assertions describe required behavior.

Run: python3 -m unittest discover -s out/tests -t .
No network, real entitlement commands or production journals.
"""
from dataclasses import replace
from datetime import timedelta
import threading
import time
from types import SimpleNamespace
from unittest.mock import patch

from gate.model import IN
from gate.tests.review4.support import Case, NOW, Live, conv, flow, grant, invite, msg, policy, withdraw
from gate.tests.review7.test_round7 import CheckedSender


EMAIL = 'ada@example.com'


class PremiumGuard(Case):
    def setup_premium(self, sender_class=CheckedSender):
        t = policy.load()['app-access']
        source = Live(conv(msg('email', EMAIL, direction=IN)))
        sender = sender_class(source)
        current = self.contract(status='active')
        g = self.gate(types={t.id: t}, source=source, sender=sender, reader=lambda cid: dict(current))
        a = self.action(message_type=t.id, fields={'email': EMAIL}, contract=dict(current))
        return g, a, source, sender, current

    def test_Y01_slow_pregrant_preflight_cannot_outlive_contract_evidence(self):
        elapsed, preflights, mutations = [1000.0], [], []
        current = {}

        class SlowPreflight(CheckedSender):
            def preflight(inner, action):
                preflights.append(1)
                super().preflight(action)
                if len(preflights) == 3:  # _pre_grant AFTER the bounded final recheck
                    current['status'] = 'cancelled'
                    elapsed[0] += 45.0  # route/person verification is explicit remote I/O

        g, a, source, sender, state = self.setup_premium(SlowPreflight)
        current = state
        g.now = lambda: NOW + timedelta(seconds=elapsed[0] - 1000)

        def runner(args, **kw):
            if args[1] == 'grant':
                mutations.append(args)
            word = 'NONE' if args[1] == 'check' else 'GRANTED'
            return SimpleNamespace(returncode=0, stdout=f'{word}: {EMAIL}', stderr='')

        g.granter = lambda action: grant.grant(self.j, action.creator_key, EMAIL, 'offline', runner)
        with patch('time.monotonic', side_effect=lambda: elapsed[0]):
            result = g.run(a)
        self.assertGreaterEqual(len(preflights), 3)
        self.assertEqual(result.outcome, 'held')
        self.assertEqual(sender.delivered, [])
        self.assertEqual(mutations, [], 'Contract evidence is 45s old before grant; the span ends before preflight')

    def test_Y01_sqlite_contention_after_guard_cannot_outlive_contract_evidence(self):
        # Real WAL connections and a real BEGIN IMMEDIATE wait, not a fake settle_premium implementation.
        # The writer gets its lock only at pre-grant preflight, after Gate has taken its own leases.
        from gate.journal import Journal
        self.j = self.new_journal(self.root / 'contended.db')
        current, acquired, release, errors, workers, preflights, mutations = {}, threading.Event(), threading.Event(), [], [], [], []

        def competing_writer():
            other = Journal(self.root / 'contended.db')
            try:
                other.conn.execute('BEGIN IMMEDIATE')
                current['status'] = 'cancelled'
                acquired.set()
                release.wait(12.0)
                other.conn.execute('COMMIT')
            except BaseException as exc:
                errors.append(exc)
                acquired.set()
            finally:
                other.conn.close()

        class ContendedPreflight(CheckedSender):
            def preflight(inner, action):
                preflights.append(1)
                super().preflight(action)
                if len(preflights) == 3:
                    worker = threading.Thread(target=competing_writer)
                    workers.append(worker)
                    worker.start()
                    if not acquired.wait(5):
                        raise AssertionError('The test writer did not acquire its transaction')

        g, a, source, sender, state = self.setup_premium(ContendedPreflight)
        current = state

        def runner(args, **kw):
            if args[1] == 'grant':
                mutations.append(args)
            word = 'NONE' if args[1] == 'check' else 'GRANTED'
            return SimpleNamespace(returncode=0, stdout=f'{word}: {EMAIL}', stderr='')

        g.granter = lambda action: grant.grant(self.j, action.creator_key, EMAIL, 'offline', runner)
        started = time.monotonic()
        try:
            result = g.run(a)
        finally:
            release.set()
            for worker in workers:
                worker.join(5)
        self.assertEqual(errors, [])
        self.assertGreater(time.monotonic() - started, 10)
        self.assertEqual(result.outcome, 'held')
        self.assertEqual(mutations, [], 'BEGIN IMMEDIATE waits 12s after the guard, then grants on stale evidence')

    def test_Y02_active_entitlement_cannot_claim_owner_after_contract_cancelled(self):
        g, a, source, sender, current = self.setup_premium()
        elapsed = [1000.0]
        g.now = lambda: NOW + timedelta(seconds=elapsed[0] - 1000)

        def runner(args, **kw):
            self.assertEqual(args[1], 'check')
            current['status'] = 'cancelled'
            elapsed[0] += 45.0
            return SimpleNamespace(returncode=0, stdout=f'ACTIVE: {EMAIL}', stderr='')

        g.granter = lambda action: grant.grant(self.j, action.creator_key, EMAIL, 'offline', runner)
        with patch('time.monotonic', side_effect=lambda: elapsed[0]):
            result = g.run(a)
        self.assertEqual(result.outcome, 'held')
        self.assertEqual(sender.delivered, [])
        self.assertEqual(self.j.premium_owners(EMAIL), set(),
                         'ACTIVE bypasses the guard and permanently assigns an ineligible creator this email')


class DurableSigning(Case):
    def writer(self, writes):
        return SimpleNamespace(request=lambda *args, **kw: writes.append((args, kw)) or
                               {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})

    def test_Y03_signing_seen_by_gate_during_draft_flow_cannot_be_erased_before_withdrawal(self):
        old_invite = invite(at=NOW - timedelta(hours=7))
        request = msg('request', '📨 Requested 2 handles for this contract.',
                      direction=IN, at=NOW - timedelta(hours=6))
        source = Live(conv(old_invite, request))
        sender = CheckedSender(source)
        t = replace(policy.load()['contract-reminder-1'], mode='draft')
        g = self.gate(types={t.id: t}, source=source, sender=sender, reader=lambda cid: self.contract())
        g.applications_reader = lambda uid: []
        clock, writes = [NOW], []
        client = SimpleNamespace(request=lambda *args, **kw: self.contract())
        f = flow.Flow(client, source, g, self.j, lambda chat: ('route1', 'person1'), now=lambda: clock[0],
                      fetchers={}, write_client=self.writer(writes), read_client=SimpleNamespace(pages=lambda path: []))
        # Flow's initial read precedes the notice; Gate's newer read sees it and correctly holds the draft.
        result = f.handle(self.contract(applications=[], applications_required=True), conv(old_invite), 'sideshift:U1')
        self.assertIn('state: not_accepted is false', result[0])
        self.assertEqual(sender.delivered, [])
        # Next day the request has been redacted; this is persistent loss, not a read-time race.
        source.conv = conv(old_invite, replace(request, text='', kind='text', deleted=True), fp='redacted')
        clock[0] += timedelta(hours=33)
        outcome = f.handle(self.contract(applications=[], applications_required=True), source.conv, 'sideshift:U1')
        self.assertEqual(writes, [], f'The gate saw signing but did not preserve it: {outcome}')

    def test_Y03_signing_seen_by_withdrawal_cannot_be_erased_on_next_run(self):
        old_invite = invite(at=NOW - timedelta(hours=40))
        writes, apps = [], [{'id': 'req1', 'status': 'pending',
                            'requestedAt': (NOW - timedelta(hours=39)).isoformat()}]
        writer = self.writer(writes)
        first = withdraw.withdraw('C1', lambda cid: self.contract(), lambda: conv(old_invite),
                                  self.j, 'sideshift:U1', NOW, writer, lambda: list(apps))
        self.assertEqual(first[0], 'held')
        self.assertTrue(any('may have signed' in reason for reason in first[1]))
        apps.clear()  # structured record disappears before a subsequent scheduled run
        second = withdraw.withdraw('C1', lambda cid: self.contract(), lambda: conv(old_invite),
                                   self.j, 'sideshift:U1', NOW + timedelta(hours=3), writer, lambda: [])
        self.assertEqual(writes, [], f'An earlier positive withdrawal check is forgotten: {second}')

    def test_Y03_signing_seen_by_gate_cannot_be_erased_before_next_reminder(self):
        old_invite = invite(at=NOW - timedelta(hours=7))
        request = msg('request', '📨 Requested 2 handles for this contract.',
                      direction=IN, at=NOW - timedelta(hours=6))
        source = Live(conv(old_invite, request))
        sender = CheckedSender(source)
        t = policy.load()['contract-reminder-1']
        g = self.gate(types={t.id: t}, source=source, sender=sender,
                      reader=lambda cid: self.contract())
        g.applications_reader = lambda uid: []
        first = g.run(self.action(message_type=t.id, fields={'First': 'Ada'}))
        self.assertIn('state: not_accepted is false', first.reasons)
        source.conv = conv(old_invite, replace(request, text='', kind='text', deleted=True), fp='redacted')
        g.now = lambda: NOW + timedelta(hours=3)
        second = g.run(self.action(message_type=t.id, fields={'First': 'Ada'}))
        self.assertEqual(sender.delivered, [], f'Reminders resume three hours after signing was seen: {second.outcome}')
