"""Offline counterexamples: assertions state required behavior and intentionally fail.

Run: python3 -m unittest discover -s out/tests -t .
Private SQLite journals, fake clocks, fake entitlement commands and real gate/transport code.
"""
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from gate.dispatch import text_hash
from gate.model import Decision, IN
from gate.tests.review4.support import (
    Case, InboxCase, NOW, Live, conv, flow, grant, invite, msg, policy, withdraw,
)
from gate.tests.review7.test_round7 import CheckedSender


class PremiumAuthorization(Case):
    def run_changed_during_check(self, change, ordered=False):
        t = policy.load()['app-access']
        if ordered:
            path = self.root / 'app-access.md'
            path.write_text(Path(t.source).read_text().replace('mode: auto', 'mode: draft'))
            t = policy.parse(path)
        source = Live(conv(msg('email', 'ada@example.com', direction=IN)))
        sender = CheckedSender(source)
        current, clock, mutations = self.contract(status='active'), [NOW], []
        g = self.gate(types={t.id: t}, source=source, sender=sender,
                      reader=lambda cid: dict(current))
        g.now = lambda: clock[0]
        a = self.action(message_type=t.id, fields={'email': 'ada@example.com'},
                        contract=dict(current))
        lease_clock = [1000.0]
        if ordered:
            with patch('gate.journal.time.time', side_effect=lambda: lease_clock[0]):
                a.approval_id = self.j.approve(a.creator_key, t.id, a.occurrence,
                                             text_hash(policy.render(t, a.fields)), 'send once', ttl=20)
        def runner(args, **kw):
            if args[1] == 'check':
                clock[0] += timedelta(seconds=45)
                lease_clock[0] += 45
                change(current, source)
                word = 'NONE'
            else:
                mutations.append(args)
                word = 'GRANTED'
            return SimpleNamespace(returncode=0, stdout=f'{word}: ada@example.com', stderr='')
        g.granter = lambda action: grant.grant(self.j, action.creator_key, action.fields['email'], 'offline', runner)
        with patch('gate.journal.time.time', side_effect=lambda: lease_clock[0]):
            result = g.run(a)
        self.assertEqual(result.outcome, 'held')
        self.assertEqual(sender.delivered, [])
        return mutations, result

    def test_X01_cancelled_contract_during_entitlement_check_cannot_grant(self):
        mutations, result = self.run_changed_during_check(lambda current, source: current.update(status='cancelled'))
        self.assertEqual(mutations, [], f'45-second-old active contract authorizes Premium: {result.reasons}')

    def test_X01_dnc_during_entitlement_check_cannot_grant(self):
        def restrict(current, source):
            self.j.event('sideshift:U1', 'do-not-contact', 'during-check', {'enabled': True})
        mutations, result = self.run_changed_during_check(restrict)
        self.assertEqual(mutations, [], f'DNC is noticed only after Premium mutation: {result.reasons}')

    def test_X01_email_removed_during_entitlement_check_cannot_grant(self):
        def retract(current, source):
            source.conv = conv(msg('email', 'Please wait before setting up my account.', direction=IN), fp='edited')
        mutations, result = self.run_changed_during_check(retract)
        self.assertEqual(mutations, [], f'Retracted email still authorizes Premium: {result.reasons}')

    def test_X01_captain_approval_expiring_during_check_cannot_grant(self):
        mutations, result = self.run_changed_during_check(lambda *a: None, ordered=True)
        self.assertEqual(mutations, [], f'Expired approval still authorizes Premium: {result.reasons}')


class PremiumOwnership(Case):
    def test_X02_overlapping_active_checks_cannot_confirm_two_owners(self):
        email, nested = 'ada@example.com', []
        other = self.new_journal(self.root / 'account.db')
        first = self.new_journal(self.root / 'account.db')
        active = lambda *a, **kw: SimpleNamespace(returncode=0, stdout=f'ACTIVE: {email}', stderr='')
        def delayed_check(args, **kw):
            # U1 read no owner before remote I/O; U2 completes on another SQLite connection meanwhile.
            nested.append(grant.grant(other, 'sideshift:U2', email, 'second creator', active))
            return active()
        ok, line = grant.grant(first, 'sideshift:U1', email, 'first creator', delayed_check)
        self.assertTrue(nested[0][0])
        self.assertFalse(ok, f'U1 ignores U2 ownership established during check: {line}')

    def test_X02_active_acknowledgment_during_none_check_cannot_allow_regrant(self):
        email, mutations = 'ada@example.com', []
        other = self.new_journal(self.root / 'revoked.db')
        first = self.new_journal(self.root / 'revoked.db')
        def runner(args, **kw):
            if args[1] == 'check':
                active = lambda *a, **kw: SimpleNamespace(returncode=0, stdout=f'ACTIVE: {email}', stderr='')
                self.assertTrue(grant.grant(other, 'sideshift:U2', email, 'existing entitlement', active)[0])
                # It is revoked while U1's remote check is in progress. U1 receives current NONE.
                word = 'NONE'
            else:
                mutations.append(args)
                word = 'GRANTED'
            return SimpleNamespace(returncode=0, stdout=f'{word}: {email}', stderr='')
        ok, line = grant.grant(first, 'sideshift:U1', email, 'stale owner snapshot', runner)
        self.assertEqual(mutations, [], f'Account already acknowledged by U2 is re-granted by U1: {ok}, {line}')


class HistoricalSigning(Case):
    def remember_signing(self, history):
        f = flow.Flow(None, Live(history), None, self.j, lambda chat: ('route1', 'person1'),
                      now=lambda: NOW, fetchers={})
        f.handle(self.contract(applications=[], applications_required=True), history, 'sideshift:U1')
        self.assertIn('C1', self.j.flags('sideshift:U1', 'maybe-signed'))

    def test_V04_redacted_notice_cannot_erase_journaled_signing_before_withdrawal(self):
        old_invite = invite(at=NOW - timedelta(hours=40))
        request = msg('request', '📨 Requested 2 handles for this contract.',
                      direction=IN, at=NOW - timedelta(hours=39))
        self.remember_signing(conv(old_invite, request))
        redacted = replace(request, text='', kind='text', deleted=True)
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        result = withdraw.withdraw('C1', lambda cid: self.contract(), lambda: conv(old_invite, redacted),
                                   self.j, 'sideshift:U1', NOW, writer, lambda: [])
        self.assertEqual(writes, [], f'An existing maybe-signed fact is ignored: {result}')

    def test_V04_redacted_notice_cannot_resume_automatic_reminders(self):
        old_invite = invite(at=NOW - timedelta(hours=7))
        request = msg('request', '📨 Requested 2 handles for this contract.',
                      direction=IN, at=NOW - timedelta(hours=6))
        self.remember_signing(conv(old_invite, request))
        source = Live(conv(old_invite, replace(request, text='', kind='text', deleted=True)))
        sender = CheckedSender(source)
        t = policy.load()['contract-reminder-1']
        g = self.gate(types={t.id: t}, source=source, sender=sender, reader=lambda cid: self.contract())
        g.applications_reader = lambda uid: []
        result = g.run(self.action(message_type=t.id, fields={'First': 'Ada'}))
        self.assertEqual(sender.delivered, [], f'Historical signing ignored by reminder: {result.outcome}')


class DraftCoverage(InboxCase):
    def test_X03_old_unrelated_template_cannot_settle_a_new_email_in_draft_mode(self):
        t = policy.load()['at-capacity']
        a = self.action(message_type=t.id, fields={'First': 'Ada'}, contract=self.contract(status='active'))
        self.j.record(a, self.gate(types={t.id: t}).key(t, a),
                      Decision('sent', ['previous capacity reply'], policy.render(t, a.fields)))
        types = {k: replace(v, mode='draft') for k, v in policy.load().items()}
        source = Live(conv(msg('email', 'ada@example.com', direction=IN)))
        with patch.object(policy, 'load', return_value=types):
            self.run_inbox(items=[{'id': 'in1', 'external_id': 'sideshift:email', 'channel': 'sideshift',
                                   'conversation_id': 'route1', 'text': 'ada@example.com'}], source=source,
                           proposals=[{'message_id': 'in1', 'action': 'template', 'message_type': t.id}])
        self.assertEqual(self.sent, [])
        self.assertEqual(self.external, [])
        self.assertEqual(self.marked[0]['outcome'], 'escalated',
                         'A live id/text match plus an unrelated old send does not prove this email was handled')


class EvidenceClock(Case):
    def test_X04_clock_rollback_cannot_hide_slow_final_evidence_read(self):
        t = policy.load()['warmup-guide']
        current = self.contract(status='active')
        wall, elapsed, reads = [NOW], [1000.0], []
        class Source(Live):
            def read(inner, *a, **kw):
                reads.append('chat')
                if len(reads) == 4:
                    elapsed[0] += 120.0
                    # A two-minute read plus a two-minute OS clock rollback: wall time is unchanged.
                    wall[0] += timedelta(seconds=120)
                    wall[0] -= timedelta(seconds=120)
                    current['status'] = 'cancelled'
                return inner.conv
        source = Source()
        sender = CheckedSender(source)
        g = self.gate(types={t.id: t}, source=source, sender=sender, reader=lambda cid: dict(current))
        g.now = lambda: wall[0]
        with patch('time.monotonic', side_effect=lambda: elapsed[0]):
            result = g.run(self.action(message_type=t.id, fields={'First': 'Ada'},
                                       contract=self.contract(status='active')))
        self.assertEqual(len(reads), 4)
        self.assertEqual(elapsed[0] - 1000.0, 120.0)
        self.assertEqual(sender.delivered, [], f'Wall-clock rollback defeats the 10-second bound: {result.outcome}')
