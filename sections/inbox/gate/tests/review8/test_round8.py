"""Offline counterexamples: assertions express required behavior and intentionally fail.

Run: python3 -m unittest discover -s out/tests -t .
No network, credentials, production journals or real grant commands are used.
"""
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from gate import checks
from gate.model import Decision, IN
from gate.tests.review4.support import (
    Case, InboxCase, NOW, Live, Sender, conv, grant, invite, msg, policy, withdraw,
)
from gate.tests.review7.test_round7 import CheckedSender


class FinalBoundary(Case):
    def test_V01_healthy_real_transport_can_send_a_reminder_with_a_gap(self):
        t = policy.load()['contract-reminder-1']
        source = Live(conv(invite(at=NOW - timedelta(hours=7))))
        sender = CheckedSender(source)
        g = self.gate(types={t.id: t}, source=source, sender=sender,
                      reader=lambda cid: self.contract())
        g.applications_reader = lambda uid: []
        with patch('gate.journal.datetime') as journal_time:
            journal_time.now.return_value = NOW
            result = g.run(self.action(message_type=t.id, fields={'First': 'Ada'}))
        self.assertEqual(result.outcome, 'sent',
                         f'A clean first send must not count its own dispatch intent as a recent send: {result.reasons}')

    def test_V01_healthy_real_transport_can_request_email_with_a_gap(self):
        t = policy.load()['ask-app-email']
        source = Live(conv(invite(at=NOW - timedelta(hours=7))))
        sender = CheckedSender(source)
        g = self.gate(types={t.id: t}, source=source, sender=sender,
                      reader=lambda cid: self.contract(status='active'))
        with patch('gate.journal.datetime') as journal_time:
            journal_time.now.return_value = NOW
            result = g.run(self.action(message_type=t.id, contract=self.contract(status='active')))
        self.assertEqual(result.outcome, 'sent', f'The final recheck blocks its own 30-minute gap: {result.reasons}')

    def test_V02_expiry_during_final_contract_read_must_prevent_delivery(self):
        t = policy.load()['warmup-guide']  # actual automatic type, zero minimum gap
        source = Live()
        sender = CheckedSender(source)
        clock, reads = [1000.0], []
        def read_contract(cid):
            reads.append(cid)
            if len(reads) == 2:  # transport's recheck, AFTER Gate's last ownership check
                clock[0] += 901  # process suspended during remote I/O; leases last 900 seconds
            return self.contract(status='active')
        g = self.gate(types={t.id: t}, source=source, sender=sender, reader=read_contract)
        with patch('gate.journal.time.time', side_effect=lambda: clock[0]):
            result = g.run(self.action(message_type=t.id, fields={'First': 'Ada'},
                                       contract=self.contract(status='active')))
        self.assertEqual(len(reads), 2)
        self.assertEqual(sender.delivered, [], f'An expired worker delivered after an explicit slow read: {result.outcome}')

    def test_U03_chat_change_during_final_contract_io_is_not_a_split_second(self):
        t = policy.load()['warmup-guide']
        source = Live()
        sender = CheckedSender(source)
        reads, clock = [], [NOW]
        def read_contract(cid):
            reads.append(cid)
            if len(reads) == 2:
                clock[0] += timedelta(minutes=2)
                source.conv = conv(invite(), msg('new-question', 'Please wait. What are the payment terms?',
                                                 at=clock[0], direction=IN), fp='new-chat')
            return self.contract(status='active')
        g = self.gate(types={t.id: t}, source=source, sender=sender, reader=read_contract)
        g.now = lambda: clock[0]
        result = g.run(self.action(message_type=t.id, fields={'First': 'Ada'},
                                   contract=self.contract(status='active')))
        self.assertEqual(len(reads), 2)
        self.assertTrue(checks.unanswered(source.conv))
        self.assertEqual(sender.delivered, [], f'Two minutes of I/O after the final chat read: {result.outcome}')


class PolicyEffects(Case):
    def test_U04_off_switch_must_stop_premium_mutation_too(self):
        original = policy.load()['app-access']
        path = self.root / 'app-access.md'
        path.write_text(Path(original.source).read_text())
        t = policy.parse(path)
        effects = []
        source = Live(conv(msg('email', 'ada@example.com', direction=IN)))
        def reviewer(*args):
            path.write_text(path.read_text().replace('mode: auto', 'mode: off'))
            return 'SEND', 'review was started before the switch', []
        g = self.gate(types={t.id: t}, source=source, reviewer=reviewer,
                      reader=lambda cid: self.contract(status='active'))
        g.granter = lambda action: (effects.append(action.fields['email']) or True, 'GRANTED')
        result = g.run(self.action(message_type=t.id, fields={'email': 'ada@example.com'},
                                   contract=self.contract(status='active')))
        self.assertEqual(result.outcome, 'held')  # send is stopped, but the account was already changed
        self.assertEqual(effects, [], 'The current off policy is checked only AFTER the grant')


class PremiumOwnership(Case):
    def test_V03_preexisting_active_account_cannot_be_regranted_through_another_creator(self):
        email, mutations = 'ada@example.com', []
        active = [True]
        def runner(args, **kw):
            if args[1] == 'check':
                word = 'ACTIVE' if active[0] else 'NONE'
            else:
                mutations.append(args)
                word = 'GRANTED'
            return SimpleNamespace(returncode=0, stdout=f'{word}: {email}', stderr='')
        ok, _ = grant.grant(self.j, 'sideshift:U1', email, 'first creator', runner)
        self.assertTrue(ok)
        self.assertTrue(self.j.premium_granted('sideshift:U1', email))
        active[0] = False  # previously acknowledged entitlement is now revoked
        ok, line = grant.grant(self.j, 'sideshift:U2', email, 'second creator', runner)
        self.assertEqual(mutations, [], f'ACTIVE never claimed account ownership; another creator restores it: {line}')


class SigningEvidence(Case):
    def test_V04_rejected_handle_request_still_proves_she_requested_handles(self):
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        apps = [{'id': 'req1', 'status': 'rejected', 'requestedAt': (NOW - timedelta(hours=39)).isoformat()}]
        withdraw.withdraw('C1', lambda cid: self.contract(),
                          lambda: conv(invite(at=NOW - timedelta(hours=40))), self.j,
                          'sideshift:U1', NOW, writer, lambda: apps)
        self.assertEqual(writes, [], 'The brief says ANY handle request since the FIRST invite blocks withdrawal')


class InboxVisibility(InboxCase):
    def test_S11_notification_address_is_not_proof_a_complaint_is_machine_mail(self):
        types = {k: replace(t, mode='draft') for k, t in policy.load().items()}
        with patch.object(policy, 'load', return_value=types):
            self.run_inbox(items=[{'id': 'in1', 'channel': 'email', 'conversation_id': 'route1',
                                   'handle': {'value_normalized': 'notifications@creator-agency.example'},
                                   'text': 'This is Ada. Your automatic reply gave me the wrong rate. Payment overdue.'}],
                           proposals=[{'message_id': 'in1', 'action': 'ignore', 'reason': 'notification sender'}])
        self.assertEqual(self.marked[0]['outcome'], 'escalated',
                         'An address local-part is still a heuristic, even when a human complaint is explicit')

    def test_S10_unlisted_media_is_not_covered_by_an_old_email_reply(self):
        t = policy.load()['app-access']
        a = self.action(message_type=t.id, fields={'email': 'ada@example.com'},
                        contract=self.contract(status='active'))
        self.j.record(a, self.gate(types={t.id: t}).key(t, a),
                      Decision('sent', ['previous reply'], policy.render(t, a.fields)))
        # The cached inbox text need not include attachment metadata; live evidence has new media.
        types = {k: replace(v, mode='draft') for k, v in policy.load().items()}
        with patch.object(policy, 'load', return_value=types):
            self.run_inbox(items=[{'id': 'in1', 'external_id': 'sideshift:photo2', 'channel': 'sideshift',
                                   'conversation_id': 'route1', 'text': 'ada@example.com'}],
                           source=Live(conv(msg('photo2', 'ada@example.com', direction=IN,
                                                attachments=1, attachments_sig='unreviewed'))))
        self.assertEqual(self.marked[0]['outcome'], 'escalated',
                         'The spent-key fast path never reads live media; omitted metadata settles unseen work')
