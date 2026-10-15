"""Offline counterexamples. Assertions describe required behavior and intentionally fail.

Run: python3 -m unittest discover -s out/tests -t .
All transports, clocks, model verdicts, Premium commands and journals are private fakes.
"""
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from gate.model import Decision, IN
from gate.tests.review4.support import (
    Case, InboxCase, NOW, Live, conv, grant, invite, msg, policy, withdraw,
)
from gate.tests.review7.test_round7 import CheckedSender


class WithdrawalEvidence(Case):
    def test_V04_deleted_handle_notice_is_still_historical_signing_evidence(self):
        writes = []
        history = conv(invite(at=NOW - timedelta(hours=40)),
                       msg('old-request', '📨 Requested 2 handles for this contract.',
                           at=NOW - timedelta(hours=39), direction=IN, deleted=True))
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        result = withdraw.withdraw('C1', lambda cid: self.contract(), lambda: history,
                                   self.j, 'sideshift:U1', NOW, writer, lambda: [])
        self.assertEqual(writes, [], f'Deleting a notice erased a request since the first invite: {result}')

    def test_W01_handle_request_during_slow_chat_read_prevents_withdrawal(self):
        """Requests can exist while the contract is still pending, with no chat notice yet."""
        clock, apps, writes = [NOW], [], []
        def read_apps():
            return list(apps)
        def read_chat():
            clock[0] += timedelta(minutes=2)
            apps.append({'id': 'new-request', 'status': 'pending',
                         'requestedAt': clock[0].isoformat()})
            return conv(invite(at=NOW - timedelta(hours=40)))
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        result = withdraw.withdraw('C1', lambda cid: self.contract(), read_chat,
                                   self.j, 'sideshift:U1', NOW, writer, read_apps)
        self.assertTrue(apps)
        self.assertEqual(writes, [], f'Two-minute-old application evidence authorized rejection: {result}')


class FinalEvidence(Case):
    def test_U03_contract_cancelling_during_last_chat_read_prevents_warmup(self):
        """Round 9 adds a fourth chat read AFTER the last contract GET."""
        t = policy.load()['warmup-guide']
        current, clock, reads = self.contract(status='active'), [NOW], []
        class SlowLastRead(Live):
            def read(inner, *a, **kw):
                reads.append('chat')
                if len(reads) == 4:
                    clock[0] += timedelta(minutes=2)
                    current['status'] = 'cancelled'
                return inner.conv
        source = SlowLastRead()
        sender = CheckedSender(source)
        g = self.gate(types={t.id: t}, source=source, sender=sender,
                      reader=lambda cid: dict(current))
        g.now = lambda: clock[0]
        result = g.run(self.action(message_type=t.id, fields={'First': 'Ada'},
                                   contract=self.contract(status='active')))
        self.assertEqual(len(reads), 4)
        self.assertEqual(current['status'], 'cancelled')
        self.assertEqual(sender.delivered, [], f'The last contract read is stale across explicit I/O: {result.outcome}')

    def test_W02_changed_minimum_gap_is_enforced_before_send(self):
        original = policy.load()['warmup-guide']
        path = self.root / 'warmup-guide.md'
        path.write_text(Path(original.source).read_text())
        t = policy.parse(path)
        source = Live(conv(invite(), msg('captain-recent', 'I will get back to you shortly.',
                                        at=NOW - timedelta(minutes=1), author='captain')))
        sender = CheckedSender(source)
        def reviewer(*a):
            path.write_text(path.read_text().replace('min_gap_minutes: 0', 'min_gap_minutes: 180'))
            return 'SEND', 'started with old policy', []
        g = self.gate(types={t.id: t}, source=source, sender=sender, reviewer=reviewer,
                      reader=lambda cid: self.contract(status='active'))
        result = g.run(self.action(message_type=t.id, fields={'First': 'Ada'},
                                   contract=self.contract(status='active')))
        self.assertEqual(policy.parse(path).min_gap_minutes, 180)
        self.assertEqual(sender.delivered, [], f'Policy reload ignores changed safety fields: {result.outcome}')


class PremiumEffects(Case):
    def test_W03_off_switch_during_read_only_entitlement_check_prevents_grant(self):
        """The real helper performs remote check I/O after Gate's last pre-grant policy check."""
        original = policy.load()['app-access']
        path = self.root / 'app-access.md'
        path.write_text(Path(original.source).read_text())
        t = policy.parse(path)
        mutations, clock = [], [NOW]
        def runner(args, **kw):
            if args[1] == 'check':
                clock[0] += timedelta(seconds=45)
                path.write_text(path.read_text().replace('mode: auto', 'mode: off'))
                word = 'NONE'
            else:
                mutations.append(args)
                word = 'GRANTED'
            return SimpleNamespace(returncode=0, stdout=f'{word}: ada@example.com', stderr='')
        g = self.gate(types={t.id: t}, source=Live(conv(msg('email', 'ada@example.com', direction=IN))),
                      reader=lambda cid: self.contract(status='active'))
        g.now = lambda: clock[0]
        g.granter = lambda a: grant.grant(self.j, a.creator_key, a.fields['email'], 'offline', runner)
        result = g.run(self.action(message_type=t.id, fields={'email': 'ada@example.com'},
                                   contract=self.contract(status='active')))
        self.assertEqual(policy.parse(path).mode, 'off')
        self.assertEqual(mutations, [], f'Off is noticed only after the irreversible grant: {result.reasons}')

    def test_V03_legacy_receipt_prevents_regrant_via_another_creator(self):
        """Pre-account-ownership journals contain creator receipts without premium:<email> events."""
        email, mutations = 'ada@example.com', []
        self.grant_receipt(email)
        def runner(args, **kw):
            if args[1] == 'grant':
                mutations.append(args)
            word = 'NONE' if args[1] == 'check' else 'GRANTED'
            return SimpleNamespace(returncode=0, stdout=f'{word}: {email}', stderr='')
        ok, line = grant.grant(self.j, 'sideshift:U2', email, 'second creator', runner)
        self.assertEqual(mutations, [], f'Legacy U1 receipt is invisible to U2: {ok}, {line}')

    def test_W04_active_account_cannot_be_acknowledged_for_two_creators(self):
        email = 'ada@example.com'
        runner = lambda *a, **kw: SimpleNamespace(returncode=0, stdout=f'ACTIVE: {email}', stderr='')
        self.assertTrue(grant.grant(self.j, 'sideshift:U1', email, 'first creator', runner)[0])
        ok, line = grant.grant(self.j, 'sideshift:U2', email, 'second creator', runner)
        self.assertFalse(ok, f'One owner per email is not enforced on ACTIVE: {line}')
        self.assertFalse(self.j.premium_granted('sideshift:U2', email))


class InboxCoverage(InboxCase):
    def test_S10_old_plain_message_cannot_cover_a_different_edited_inbound(self):
        t = policy.load()['app-access']
        a = self.action(message_type=t.id, fields={'email': 'ada@example.com'},
                        contract=self.contract(status='active'))
        self.j.record(a, self.gate(types={t.id: t}).key(t, a),
                      Decision('sent', ['old reply'], policy.render(t, a.fields)))
        # Cache still has the target's old email-only revision. Live has the edited target AND an old plain email.
        source = Live(conv(msg('old-email', 'ada@example.com', direction=IN),
                           msg('target', 'Please review my draft.', direction=IN,
                               attachments=1, attachments_sig='new-draft')))
        types = {k: replace(v, mode='draft') for k, v in policy.load().items()}
        with patch.object(policy, 'load', return_value=types):
            self.run_inbox(items=[{'id': 'in1', 'external_id': 'sideshift:target', 'channel': 'sideshift',
                                   'conversation_id': 'route1', 'text': 'ada@example.com'}], source=source)
        self.assertEqual(self.marked[0]['outcome'], 'escalated',
                         'A different old text match settles the edited inbound without inspecting its media')

