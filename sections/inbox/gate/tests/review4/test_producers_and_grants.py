import json
import sys
import types
from dataclasses import replace
from contextlib import ExitStack, redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from gate import checks
from gate.model import Decision, IN
from .support import Case, InboxCase, NOW, Live, Sender, conv, flow, grant, invite, msg, policy, propose
import record


class InboxBoundaries(InboxCase):
    def test_R09_uncertain_send_is_not_settled_as_done_on_next_inbox_run(self):
        a = self.action(message_type='app-access', fields={'email': 'ada@example.com'}, contract=self.contract(status='active'))
        key = self.gate(types=policy.load()).key(policy.load()['app-access'], a)
        self.j.record(a, key, Decision('uncertain', ['timeout after request left']))
        self.run_inbox()
        self.assertEqual(self.marked[0]['outcome'], 'escalated', 'Spent means may have sent, not verified completion')

    def test_R09_old_email_receipt_cannot_settle_a_new_email_request(self):
        a = self.action(message_type='app-access', fields={'email': 'old@example.com'}, contract=self.contract(status='active'))
        key = self.gate(types=policy.load()).key(policy.load()['app-access'], a)
        self.j.record(a, key, Decision('sent', ['sent to old email'], 'old email notification'))
        self.run_inbox()  # the new inbound explicitly supplies ada@example.com
        self.assertEqual(self.marked[0]['outcome'], 'escalated', 'No payload or inbound coverage comparison before done')

    def test_R09_new_pay_question_is_not_completed_by_old_once_per_creator_reply(self):
        a = self.action(message_type='app-access', contract=self.contract(status='active'))
        key = self.gate(types=policy.load()).key(policy.load()['app-access'], a)
        self.j.record(a, key, Decision('sent', ['previous email reply']))
        self.run_inbox(source=Live(conv(msg('new-question', 'ada@example.com Also what is my rate?', direction=IN))))
        self.assertEqual(self.marked[0]['outcome'], 'escalated', 'Spent shortcut runs before live review of the new question')

    def test_R10_human_creator_email_cannot_be_ignored_on_model_label_alone(self):
        self.run_inbox(items=[{'id': 'in1', 'channel': 'email', 'conversation_id': 'route1',
                               'text': 'What is the agreed rate? Please reply.', 'person': {'name': 'Ada'}}],
                       proposals=[{'message_id': 'in1', 'action': 'ignore', 'reason': 'newsletter'}])
        self.assertEqual(self.marked[0]['outcome'], 'escalated', 'Being email does not establish automated-mail provenance')

    def test_R05_actual_inbox_prepare_and_flow_have_same_invite_key(self):
        types_ = policy.load()
        inbound = {'id': 'contacts-message', 'channel': 'sideshift'}
        detail = {'id': 'route1', 'participants': [{'value_normalized': 'U1', 'person_id': 'person1'}]}
        a, why = propose.build_action({'message_type': 'contract-reminder-1'}, inbound, detail, types_, 'chat1', 'Ada', [])
        a, why = propose.prepare(a, [self.contract()], self.j, 'Ada')
        produced = []
        gate = SimpleNamespace(run=lambda action: produced.append(action) or SimpleNamespace(outcome='held', reasons=[]))
        f = flow.Flow(None, None, gate, self.j, lambda chat: ('route1', 'person1'), now=lambda: NOW)
        f.handle(self.contract(), conv(invite()), 'sideshift:U1')
        keyer = self.gate(types=types_)
        t = types_['contract-reminder-1']
        self.assertEqual(keyer.key(t, a), keyer.key(t, produced[0]), 'prepare() never fills the invite generation')

    def test_R11_bad_person_shape_does_not_abort_later_inbox_messages(self):
        # Batch prompt construction extracts this shape before handler isolation begins.
        items = [{'id': 'in1', 'channel': 'sideshift', 'conversation_id': 'route1', 'person': 42},
                 {'id': 'in2', 'channel': 'sideshift', 'conversation_id': 'route1'}]
        _, error = self.no_crash(lambda: self.run_inbox(items=items, proposals=[
            {'message_id': 'in1', 'action': 'escalate'}, {'message_id': 'in2', 'action': 'escalate'}]))
        self.assertIn('in2', [m['message_id'] for m in self.marked], str(error))


class GrantBoundaries(Case):
    def test_R12_failed_read_only_check_does_not_spend_grant_forever(self):
        replies = iter(['ERROR: temporary check outage', 'NONE: ada@example.com', 'GRANTED: ada@example.com has free Premium'])
        calls = []
        def runner(args, **kw):
            calls.append(args[1])
            return SimpleNamespace(returncode=0, stdout=next(replies), stderr='')
        first = grant.grant(self.j, 'sideshift:U1', 'ada@example.com', 'note', runner)
        self.assertFalse(first[0])
        second = grant.grant(self.j, 'sideshift:U1', 'ada@example.com', 'note', runner)
        self.assertTrue(second[0], f'No grant command ever ran, but a repaired check cannot recover: {calls}')

    def test_R13_other_recipient_active_line_does_not_confirm_requested_account(self):
        def runner(*a, **kw):
            return SimpleNamespace(returncode=0, stdout='ACTIVE: other@example.com (requested ada@example.com)', stderr='')
        ok, line = grant.grant(self.j, 'sideshift:U1', 'ada@example.com', 'note', runner)
        self.assertFalse(ok, 'Merely mentioning the requested address in a different account result confirms it')

    def test_R13_nonstatus_prefix_does_not_confirm_premium(self):
        replies = iter(['NONE: ada@example.com', 'GRANTED_ERROR: ada@example.com was not granted', 'NONE: ada@example.com'])
        def runner(*a, **kw):
            return SimpleNamespace(returncode=0, stdout=next(replies), stderr='')
        self.assertFalse(grant.grant(self.j, 'sideshift:U1', 'ada@example.com', 'note', runner)[0])


class RecordCLI(Case):
    def test_R14_record_answered_command_emits_content_bound_marks(self):
        q = msg('q', 'What do I film?', direction=IN)
        source = Live(conv(q))
        client_module = types.ModuleType('client')
        class Client:
            def __init__(inner, *a):
                pass
            def pages(inner, *a, **kw):
                return []
        client_module.Client = Client
        dotenv = types.ModuleType('dotenv')
        dotenv.load_dotenv = lambda *a: None
        with ExitStack() as stack:
            stack.enter_context(patch.dict(sys.modules, {'client': client_module, 'dotenv': dotenv}))
            stack.enter_context(patch.dict('os.environ', {'SIDESHIFT_CONTRACTS_KEY': 'offline'}))
            stack.enter_context(patch.object(record, 'find_creator', return_value=('U1', 'Ada', 'chat1')))
            stack.enter_context(patch.object(record, 'Journal', return_value=self.j))
            stack.enter_context(patch('gate.live.SideShiftLive', return_value=source))
            stack.enter_context(patch.object(sys, 'argv', ['record.py', 'answered', 'Ada', 'q']))
            stack.enter_context(redirect_stdout(StringIO()))
            record.main()
        self.assertEqual(checks.unanswered(source.conv, self.j.flags('sideshift:U1', 'answered')), [],
                         'CLI reports marked answered, but writes a bare ID that the new checker never accepts')

    def test_R14_record_looked_at_command_emits_content_bound_marks(self):
        image = msg('q', 'Draft', direction=IN, attachments=1)
        client_module = types.ModuleType('client')
        client_module.Client = lambda *a: SimpleNamespace(pages=lambda *a, **kw: [])
        dotenv = types.ModuleType('dotenv'); dotenv.load_dotenv = lambda *a: None
        with ExitStack() as stack:
            stack.enter_context(patch.dict(sys.modules, {'client': client_module, 'dotenv': dotenv}))
            stack.enter_context(patch.dict('os.environ', {'SIDESHIFT_CONTRACTS_KEY': 'offline'}))
            stack.enter_context(patch.object(record, 'find_creator', return_value=('U1', 'Ada', 'chat1')))
            stack.enter_context(patch.object(record, 'Journal', return_value=self.j))
            stack.enter_context(patch('gate.live.SideShiftLive', return_value=Live(conv(image))))
            stack.enter_context(patch.object(sys, 'argv', ['record.py', 'looked-at', 'Ada', 'q']))
            stack.enter_context(redirect_stdout(StringIO()))
            record.main()
        self.assertEqual(checks.completeness(conv(image), self.j.flags('sideshift:U1', 'attachment-reviewed')), [])


class FlowDryRun(Case):
    def test_R19_flow_preview_honors_the_same_paused_switch(self):
        from gate.dispatch import Gate
        self.paused.touch()
        source = Live(conv(invite()))
        client_module = types.ModuleType('client')
        client_module.Client = lambda *a: SimpleNamespace(request=lambda *a, **kw: self.contract())
        dotenv = types.ModuleType('dotenv'); dotenv.load_dotenv = lambda *a: None
        observed = []
        contacts = SimpleNamespace(preflight=lambda action: None, call=lambda *a: [])
        def make_gate(*args, **kw):
            kw.setdefault('paused_file', self.paused)
            return Gate(*args, now=lambda: NOW, **kw)
        def make_flow(client, live, gate, journal, routes, **kw):
            def run():
                observed.append(gate.run(self.action()))
                return []
            return SimpleNamespace(run=run)
        with ExitStack() as stack:
            stack.enter_context(patch.dict(sys.modules, {'client': client_module, 'dotenv': dotenv}))
            stack.enter_context(patch.dict('os.environ', {'SIDESHIFT_CONTRACTS_KEY': 'offline'}))
            stack.enter_context(patch.object(flow, 'SideShiftLive', return_value=source))
            stack.enter_context(patch('gate.contacts.ContactsMCP', return_value=contacts))
            stack.enter_context(patch('gate.review.ClaudeReviewer', return_value=lambda *a: ('SEND', 'ok', [])))
            stack.enter_context(patch('gate.journal.snapshot', return_value=self.j))
            stack.enter_context(patch.object(flow.policy, 'load', return_value={'example': self.type}))
            stack.enter_context(patch.object(flow, 'Gate', side_effect=make_gate))
            stack.enter_context(patch.object(flow, 'Flow', side_effect=make_flow))
            stack.enter_context(patch.object(sys, 'argv', ['flow.py', '--dry-run']))
            stack.enter_context(redirect_stdout(StringIO()))
            flow.main()
        self.assertEqual(observed[0].outcome, 'held', 'Flow replaces the real pause switch with /nonexistent/PAUSED')
