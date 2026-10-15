"""Offline counterexamples; assertions describe the required safe behavior.

Run: python3 -m unittest discover -s out/tests -t .
All external effects are private fakes. No production files are changed.
"""
from contextlib import ExitStack, redirect_stdout
from dataclasses import replace
from datetime import timedelta
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch
import sys
import types

from gate import checks
from gate.dispatch import Gate, text_hash
from gate.live import SideShiftLive
from gate.model import Decision, IN
from gate.tests.review4.support import (
    Case, InboxCase, NOW, Live, Sender, contacts, conv, flow, invite, msg, policy, withdraw,
)


class ApplicationCoverage(Case):
    def make_flow(self, source, gate, read_client=None):
        contract = self.contract()
        client = SimpleNamespace(pages=lambda *a, **kw: [contract],
                                 request=lambda *a, **kw: dict(contract))
        source.client = SimpleNamespace(pages=lambda *a, **kw: [
            {'id': 'chat1', 'members': [flow.COMPANY, 'U1']}])
        return flow.Flow(client, source, gate, self.j,
                         lambda chat: ('route1', 'person1'), now=lambda: NOW,
                         read_client=read_client)

    def test_S02_no_read_key_is_unknown_in_real_flow_not_complete_empty(self):
        t = policy.load()['contract-reminder-1']
        sender = Sender()
        source = Live(conv(invite(at=NOW - timedelta(hours=7))))
        g = self.gate(types={t.id: t}, source=source, sender=sender,
                      reader=lambda cid: self.contract())
        report = self.make_flow(source, g).run()
        self.assertEqual(sender.calls, [], f'No application reader nevertheless authorizes reminder: {report}')

    def test_T01_configured_flow_can_refresh_and_send_proven_unsigned_reminder(self):
        # Invoke the real production composition, not a reproduction of its constructor arguments.
        sender = Sender()
        source = Live(conv(invite(at=NOW - timedelta(hours=7))))
        source.client = SimpleNamespace(pages=lambda *a, **kw: [
            {'id': 'chat1', 'members': [flow.COMPANY, 'U1']}])
        reads = []
        class Client:
            def __init__(inner, key=None):
                pass
            def pages(inner, path, **kw):
                if path == '/applications':
                    reads.append(path)
                    return []
                return [self.contract()]
            def request(inner, *a, **kw):
                return self.contract()
        client_module, dotenv = types.ModuleType('client'), types.ModuleType('dotenv')
        client_module.Client = Client
        dotenv.load_dotenv = lambda *a: None
        real_flow = flow.Flow
        def gate(*a, **kw):
            return Gate(*a, **{**kw, 'now': lambda: NOW, 'paused_file': self.paused})
        def scheduled_flow(*a, **kw):
            return real_flow(*a, **{**kw, 'now': lambda: NOW})
        with ExitStack() as stack:
            stack.enter_context(patch.dict(sys.modules, {'client': client_module, 'dotenv': dotenv}))
            stack.enter_context(patch.dict('os.environ', {'SIDESHIFT_CONTRACTS_KEY': 'offline-contracts',
                                                        'SIDESHIFT_READ_KEY': 'offline-read'}))
            stack.enter_context(patch.object(sys, 'argv', ['flow.py']))
            stack.enter_context(patch.object(flow, 'Journal', return_value=self.j))
            stack.enter_context(patch.object(flow, 'SideShiftLive', return_value=source))
            stack.enter_context(patch.object(flow, 'Gate', side_effect=gate))
            stack.enter_context(patch.object(flow, 'Flow', side_effect=scheduled_flow))
            stack.enter_context(patch.object(flow, 'contacts_routes', return_value=lambda chat: ('route1', 'person1')))
            stack.enter_context(patch.object(contacts, 'ContactsMCP', return_value=sender))
            stack.enter_context(patch('gate.review.ClaudeReviewer', return_value=lambda *a: ('SEND', 'offline review', [])))
            report = stack.enter_context(redirect_stdout(StringIO()))
            flow.main()
        self.assertEqual(len(sender.calls), 1,
                         f'A healthy configured reader is never connected to Gate; holds forever: {report.getvalue()}; reads={reads}')


class EffectFreshness(Case):
    def test_S03_contract_activating_during_live_chat_read_cannot_be_rejected(self):
        current = self.contract()
        writes = []
        def read_chat():
            # An explicit read (membership + paginated history in production), not the final request instant.
            current['status'] = 'active'
            return conv(invite(at=NOW - timedelta(hours=40)))
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        withdraw.withdraw('C1', lambda cid: dict(current), read_chat, self.j,
                          'sideshift:U1', NOW, writer, lambda: [])
        self.assertEqual(writes, [], 'Contract freshness is still lost across the subsequent live-chat fetch')

    def test_T02_contract_activating_during_gate_application_fetch_cannot_get_reminder(self):
        t = replace(self.type, requires=('contract_open', 'not_accepted'))
        current = self.contract(applications=[], applications_required=True)
        def applications(uid):
            current['status'] = 'active'
            return []
        sender = Sender()
        g = self.gate(types={t.id: t}, sender=sender, reader=lambda cid: dict(current))
        g.applications_reader = applications
        g.run(self.action(contract=current))
        self.assertEqual(sender.calls, [], 'The new application refresh leaves the preceding contract GET stale')


class InboxCoverage(InboxCase):
    def test_S10_three_word_payment_request_is_not_already_done(self):
        t = policy.load()['app-access']
        a = self.action(message_type=t.id, fields={'email': 'ada@example.com'},
                        contract=self.contract(status='active'))
        self.j.record(a, self.gate(types={t.id: t}).key(t, a),
                      Decision('sent', ['old reply'], policy.render(t, a.fields)))
        text = 'Payment overdue. ada@example.com'
        self.run_inbox(items=[{'id': 'in1', 'channel': 'sideshift',
                               'conversation_id': 'route1', 'text': text}],
                       source=Live(conv(msg('new-request', text, direction=IN))))
        self.assertEqual(self.marked[0]['outcome'], 'escalated',
                         'Word count does not establish revision-specific coverage of a new request')

    def test_S11_human_unsubscribe_must_reach_captain_even_with_all_types_draft(self):
        # Draft-only policy still runs the ignore branch and permanently marks this human request ignored.
        types = {k: replace(v, mode='draft') for k, v in policy.load().items()}
        with patch.object(policy, 'load', return_value=types):
            self.run_inbox(items=[{'id': 'in1', 'channel': 'email', 'conversation_id': 'route1',
                                   'text': 'Please unsubscribe me. Stop contacting me.'}],
                           proposals=[{'message_id': 'in1', 'action': 'ignore', 'reason': 'unsubscribe mail'}])
        self.assertEqual(self.marked[0]['outcome'], 'escalated',
                         'Unsubscribe is a human stop request, not proof of machine origin')


class AttachmentEvidence(Case):
    def source(self, raw):
        class Client:
            def pages(inner, path):
                return [{'id': 'chat1', 'members': ['COMPANY', 'U1']}] if path == '/conversations' else [raw]
        return SideShiftLive(Client(), 'COMPANY')

    def test_S15_filename_is_not_immutable_attachment_identity(self):
        raw = dict(id='photo', createdAt=(NOW - timedelta(hours=10)).isoformat(),
                   senderUserId='U1', content='Draft', updatedAt='2026-10-14T14:00:00Z',
                   attachments=[{'name': 'draft.jpg', 'url': 'https://cdn/first.jpg'}])
        source = self.source(raw)
        self.j.event('sideshift:U1', 'attachment-reviewed', checks.mark(source.read('chat1').messages[0]), {})
        raw.update(updatedAt='2026-10-14T15:00:00Z',
                   attachments=[{'name': 'draft.jpg', 'url': 'https://cdn/replacement.jpg'}])
        sender = Sender()
        self.gate(source=source, sender=sender).run(self.action())
        self.assertEqual(sender.calls, [], 'A same-filename replacement inherits review despite a new message revision')

    def test_S16_transport_url_refresh_cannot_invalidate_review_to_send_comparison(self):
        raw = dict(id='photo', createdAt=(NOW - timedelta(hours=10)).isoformat(),
                   senderUserId='U1', content='Draft',
                   attachments=[{'id': 'same-image', 'url': 'https://cdn/photo?token=one'}])
        source = self.source(raw)
        self.j.event('sideshift:U1', 'attachment-reviewed', checks.mark(source.read('chat1').messages[0]), {})
        def reviewer(*a):
            raw['attachments'][0]['url'] = 'https://cdn/photo?token=two'
            return 'SEND', 'same reviewed image', []
        sender = Sender()
        result = self.gate(source=source, sender=sender, reviewer=reviewer).run(self.action())
        self.assertEqual(result.outcome, 'sent',
                         f'Immutable review identity was fixed, but raw fingerprint still rotates: {result.reasons}')


class Authorization(Case):
    def test_S06_preclaimed_live_round_cannot_bypass_ambiguous_legacy_send(self):
        t = replace(self.type, requires=('contract_open', 'not_accepted'))
        sender = Sender()
        source = Live(conv(invite(), msg('old-send', 'Old approved wording.', at=NOW - timedelta(hours=9))))
        g = self.gate(types={t.id: t}, sender=sender, source=source)
        old = self.action(contract=self.contract(applications=[]))
        self.j.record(old, g.key(t, old), Decision('sent', ['unversioned legacy send'], 'Old approved wording.'))
        # send.py supplies inviteGeneration in advance; a producer claiming the right round is valid evidence
        # of the present round, but does not establish which round the historical send belonged to.
        a = self.action(contract=self.contract(applications=[], inviteGeneration='invite1'))
        g.run(a)
        self.assertEqual(sender.calls, [], 'A prepopulated, valid round suppresses the legacy reconciliation check')

    def test_S14_historical_receipt_without_live_checker_cannot_authorize_notification(self):
        # send.py constructs Gate without a granter. Its journal may predate a revocation.
        t = policy.load()['app-access']
        self.grant_receipt('ada@example.com')
        sender = Sender()
        source = Live(conv(msg('email', 'ada@example.com', direction=IN)))
        g = self.gate(types={t.id: t}, sender=sender, source=source,
                      reader=lambda cid: self.contract(status='active'))
        g.run(self.action(message_type=t.id, fields={'email': 'ada@example.com'},
                          contract=self.contract(status='active')))
        self.assertEqual(sender.calls, [], 'Without a live checker the old grant receipt still claims current Premium')

    def test_S07_definite_failed_receipt_restores_exact_captain_approval(self):
        t = replace(self.type, mode='off')
        aid = self.j.approve('sideshift:U1', t.id, 'C1', text_hash(t.text), 'send it')
        g = self.gate(types={t.id: t}, sender=Sender({'status': 'failed', 'error': 'definitely not sent'}))
        first = g.run(self.action(approval_id=aid))
        self.assertEqual(first.outcome, 'error')
        g.sender = Sender()
        result = g.run(self.action(approval_id=aid))
        self.assertEqual(result.outcome, 'sent', f'Definite failure releases attempt but consumes approval: {result.reasons}')

    def test_S07_lock_loss_before_request_restores_captain_approval(self):
        t = replace(self.type, mode='off')
        aid = self.j.approve('sideshift:U1', t.id, 'C1', text_hash(t.text), 'send it')
        g = self.gate(types={t.id: t})
        original = self.j.begin_attempt
        def intent(*a, **kw):
            result = original(*a, **kw)
            self.j.conn.execute('DELETE FROM reservations')
            return result
        with patch.object(self.j, 'begin_attempt', side_effect=intent):
            first = g.run(self.action(approval_id=aid))
        self.assertEqual(first.outcome, 'error')
        result = g.run(self.action(approval_id=aid))
        self.assertEqual(result.outcome, 'sent', 'A known pre-request lock loss also permanently consumes approval')


class OrderedHistory(Case):
    def test_T03_changed_same_timestamp_order_invalidates_review_and_round(self):
        at = (NOW - timedelta(hours=10)).isoformat()
        rows = [dict(id=mid, createdAt=at, senderUserId='COMPANY',
                     content='https://app.sideshift.app/campaign-invite/C1') for mid in ('round-A', 'round-B')]
        class Client:
            def pages(inner, path):
                return [{'id': 'chat1', 'members': ['COMPANY', 'U1']}] if path == '/conversations' else list(rows)
        source = SideShiftLive(Client(), 'COMPANY')
        t = replace(self.type, requires=('contract_open', 'not_accepted'))
        seen_rounds = []
        def reviewer(chat, *a):
            seen_rounds.append(checks.invite_generation(chat, self.contract()))
            rows.reverse()
            return 'SEND', 'reviewed old ordered transcript', []
        class CheckedSender(contacts.ContactsMCP):
            def __init__(inner):
                inner.live, inner.calls = source, []
            def call(inner, tool, args):
                if tool == 'get_conversation':
                    return {'id': args['conversation_id'], 'channel': 'sideshift', 'external_id': 'sideshift:chat1',
                            'participants': [{'value_normalized': 'U1', 'person_id': 'person1'}]}
                if tool == 'get_person':
                    return {'id': args['person_id'], 'handles': [], 'tags': []}
                if tool == 'send_message':
                    inner.calls.append(args)
                    return {'status': 'sent', 'id': 'out1'}
                raise AssertionError(tool)
        sender = CheckedSender()
        g = self.gate(types={t.id: t}, source=source, sender=sender, reviewer=reviewer)
        g.applications_reader = lambda uid: []   # adapted 2026-10-15: fresh, empty handle requests (review S02)
        result = g.run(self.action(contract=self.contract(applications=[])))
        self.assertEqual(seen_rounds, ['round-B'])
        self.assertEqual(checks.invite_generation(source.read('chat1'), self.contract()), 'round-A')
        self.assertEqual(sender.calls, [],
                         f'Order changed but fingerprint did not; sent using obsolete round key {result.idempotency_key}')


