import json
import sys
import types
from contextlib import ExitStack, redirect_stdout
from dataclasses import replace
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from gate.dispatch import Gate
from gate.model import IN
from .support import Case, NOW, Live, conv, contacts, grant, msg, policy, propose


class Proposals(Case):
    def run_inbox(self, proposals=None, claim=None, source=None, contract_now=None, dry=False, items=None, detail=None):
        """Invoke real main/build_action/Gate/grant against fake transports and a private journal."""
        inbox = items or [{'id': 'in1', 'channel': 'sideshift', 'conversation_id': 'route1',
                           'sent_at': NOW.isoformat(), 'text': 'ada@example.com', 'person': {'name': 'Ada'}}]
        conversation = detail or {
            'id': 'route1', 'external_id': 'sideshift:chat1', 'channel': 'sideshift',
            'participants': [{'value_normalized': 'U1', 'person_id': 'person1', 'profile': {'display_name': 'Ada'}}],
            'messages': [{'id': 'in1', 'direction': 'in', 'text': 'ada@example.com'}]}
        pending = proposals or [{'message_id': i['id'], 'action': 'template', 'message_type': 'app-access',
                                 'fields': {'email': 'ada@example.com'}} for i in inbox]
        active = self.contract(status='active')
        sent, marked, external = [], [], []
        self.sent, self.marked, self.external = sent, marked, external
        class Contacts(contacts.ContactsMCP):
            def __init__(inner):
                pass
            def call(inner, tool, args):
                if tool == 'list_inbox':
                    return {'items': inbox}
                if tool == 'claim_inbox':
                    return {'claim_token': 'ours'} if claim is None else claim
                if tool == 'get_conversation':
                    return conversation
                if tool == 'get_person':
                    return {'id': args['person_id'], 'handles': [], 'tags': []}
                if tool == 'send_message':
                    sent.append(args)
                    return {'status': 'sent', 'id': 'out1'}
                if tool == 'mark_inbox':
                    marked.append(args)
                    return {}
                raise AssertionError(tool)
        class Client:
            def __init__(inner, *a):
                pass
            def pages(inner, path, **kw):
                return [active]
            def request(inner, method, path):
                return {'data': contract_now if contract_now is not None else active}
        def run_access(args, runner):
            external.append(args)
            # adapted 2026-10-15: real output names the email; a NONE without it is not trusted (review S13)
            return ['NONE: ada@example.com has no active free Premium.' if args[0] == 'check' else 'GRANTED: ada@example.com has free Premium']
        def gate(*a, **kw):
            return Gate(*a, now=lambda: NOW, paused_file=self.paused, **kw)
        client = types.ModuleType('client')
        client.Client = Client
        dotenv = types.ModuleType('dotenv')
        dotenv.load_dotenv = lambda *a: None
        (self.root / '.claude.json').write_text(json.dumps({'mcpServers': {'contacts': {'url': 'offline://fixture'}}}))
        with ExitStack() as stack:
            stack.enter_context(patch.dict(sys.modules, {'client': client, 'dotenv': dotenv}))
            stack.enter_context(patch.dict('os.environ', {'SIDESHIFT_CONTRACTS_KEY': 'offline'}))
            stack.enter_context(patch('gate.contacts.ContactsMCP', Contacts))
            stack.enter_context(patch('gate.review.ClaudeReviewer', return_value=lambda *a: ('SEND', 'offline review', [])))
            stack.enter_context(patch.object(propose, 'HERE', self.root))
            stack.enter_context(patch('pathlib.Path.home', return_value=self.root))
            stack.enter_context(patch.object(propose, 'SideShiftLive', return_value=source or Live(conv(msg('source-in1', 'ada@example.com', direction=IN)))))
            stack.enter_context(patch.object(propose, 'ask_claude', return_value=json.dumps(pending)))
            stack.enter_context(patch.object(propose, 'Journal', return_value=self.j))
            stack.enter_context(patch.object(propose, 'snapshot', return_value=self.j))
            stack.enter_context(patch.object(propose, 'Gate', side_effect=gate))
            stack.enter_context(patch.object(grant, '_run', side_effect=run_access))
            stack.enter_context(patch.object(sys, 'argv', ['propose.py'] + (['--dry-run'] if dry else [])))
            output = stack.enter_context(redirect_stdout(StringIO()))
            _, error = self.no_crash(propose.main)
        self.output = output.getvalue()
        self.assertIsNone(error, error)
        return output.getvalue()

    def test_N02_premium_is_not_granted_while_automation_paused(self):
        self.paused.touch()
        self.run_inbox()
        self.assertEqual(self.external, [], 'check/grant executed before PAUSED is tested')

    def test_N02_premium_is_not_granted_to_dnc_creator(self):
        self.j.event('sideshift:U1', 'do-not-contact', 'captain', {'enabled': True})
        self.run_inbox()
        self.assertEqual(self.external, [], 'Grant precedes durable do-not-contact check')

    def test_N02_premium_requires_current_active_contract_before_grant(self):
        self.run_inbox(contract_now=self.contract(status='cancelled'))
        self.assertEqual(self.external, [], 'Cached active list entry grants before the fresh cancelled GET')

    def test_N02_email_provenance_must_be_live_before_grant(self):
        self.run_inbox(source=Live(conv(msg('source-in1', 'Please do not use the old email', direction=IN, attachments=1))))
        self.assertEqual(self.external, [], 'A cached email absent from live evidence causes an irreversible grant')

    def test_N03_no_claim_means_no_send_or_grant(self):
        self.run_inbox(claim={})
        self.assertEqual((self.sent, self.external), ([], []), 'Runner processes full listing without a claim token')

    def test_N03_partial_claim_does_not_authorize_unclaimed_messages(self):
        self.run_inbox(claim={'claim_token': 'token-for-someone-else', 'message_ids': ['other-message']})
        self.assertEqual((self.sent, self.external), ([], []), 'Claimed message set is ignored')

    def test_N04_creator_question_cannot_be_silently_ignored(self):
        items = [{'id': 'in1', 'channel': 'sideshift', 'conversation_id': 'route1', 'sent_at': NOW.isoformat(),
                  'text': 'How much will I be paid?', 'person': {'name': 'Ada'}}]
        self.run_inbox(proposals=[{'message_id': 'in1', 'action': 'ignore', 'reason': 'spam'}], items=items)
        self.assertEqual(self.marked[0]['outcome'], 'escalated', 'Any model-supplied reason silently settles a real creator message')

    def test_N05_parser_rejects_surrounding_text_and_duplicate_objects(self):
        for raw in ('HOLD: unsafe\n[{"message_id":"in1","action":"template","message_type":"app-access"}]',
                    '[{"message_id":"in1","action":"template"},{"message_id":"in1","action":"escalate"}]',
                    '[{"message_id":"in1","action":"escalate","action":"template"}]'):
            with self.subTest(raw=raw):
                result = propose.parse_proposals(raw, {'in1'})
                self.assertEqual(result['in1']['action'], 'escalate')

    def test_N05_malformed_field_types_escalate_without_crashing(self):
        for obj in ({'message_id': ['in1'], 'action': 'ignore'}, {'message_id': 'in1', 'action': []}):
            with self.subTest(obj=obj):
                result, error = self.no_crash(lambda: propose.parse_proposals(json.dumps([obj]), {'in1'}))
                self.assertIsNone(error, error)
                self.assertEqual(result['in1']['action'], 'escalate')

    def test_N05_failed_claude_process_cannot_propose_a_send(self):
        output = SimpleNamespace(returncode=1, stdout='[{"message_id":"in1","action":"template","message_type":"app-access"}]', stderr='failed')
        with patch.object(propose.subprocess, 'run', return_value=output):
            raw = propose.ask_claude([], policy.load())
        self.assertEqual(propose.parse_proposals(raw, {'in1'})['in1']['action'], 'escalate')

    def test_N20_bad_proposal_does_not_starve_later_message(self):
        items = [{'id': f'in{i}', 'channel': 'sideshift', 'conversation_id': 'route1', 'sent_at': NOW.isoformat()} for i in (1, 2)]
        ps = [{'message_id': 'in1', 'action': 'template', 'message_type': 'app-access', 'fields': 'wrong shape'},
              {'message_id': 'in2', 'action': 'escalate', 'summary': 'needs captain'}]
        # Explicitly inspect later work even when the current implementation raises.
        _, error = self.no_crash(lambda: self.run_inbox(proposals=ps, items=items))
        self.assertIn('in2', [m['message_id'] for m in self.marked], str(error))

    def test_N23_dry_run_performs_route_and_dnc_preflight(self):
        self.grant_receipt()
        detail = {'id': 'route1', 'external_id': 'sideshift:chat1', 'channel': 'sideshift',
                  'participants': [{'value_normalized': 'U1', 'person_id': None, 'profile': {'display_name': 'Ada'}}],
                  'messages': [{'direction': 'in', 'text': 'ada@example.com'}]}
        output = self.run_inbox(dry=True, detail=detail)
        self.assertNotIn('would send:', output, 'Fake dry sender omits the production preflight that would reject a missing person')

    def test_N23_new_premium_grant_can_be_simulated_without_real_mutation(self):
        output = self.run_inbox(dry=True)
        self.assertIn('would send:', output, 'Dry-run skips the grant but keeps the premium_granted prerequisite, always holding valid new-email work')
        self.assertEqual(self.external, [])

    def test_N24_inbox_and_flow_use_same_contract_reminder_identity(self):
        types_ = policy.load()
        detail = {'id': 'route1', 'participants': [{'value_normalized': 'U1', 'person_id': 'person1'}]}
        inbound = {'id': 'contacts-inbound', 'channel': 'sideshift'}
        proposed, why = propose.build_action({'message_type': 'contract-reminder-1'}, inbound, detail,
                                              types_, 'chat1', 'Ada', [])
        proposed.contract = self.contract(inviteGeneration='invite1')
        scheduled = replace(proposed, occurrence='C1')
        g = self.gate(types=types_)
        self.assertEqual(g.key(types_['contract-reminder-1'], proposed), g.key(types_['contract-reminder-1'], scheduled),
                         'Same reminder can be sent once per inbound plus once by Flow')

    def test_N29_one_reply_covering_two_identical_emails_settles_both(self):
        # adapted 2026-10-15 (review S10): inbox items carry their SideShift id, as contacts-mcp's real items do
        items = [{'id': f'in{i}', 'channel': 'sideshift', 'conversation_id': 'route1', 'sent_at': NOW.isoformat(),
                  'external_id': f'sideshift:default:chat1:source{i}', 'text': 'ada@example.com', 'person': {'name': 'Ada'}}
                 for i in (1, 2)]
        source = Live(conv(msg('source1', 'ada@example.com', direction=IN), msg('source2', 'ada@example.com', direction=IN)))
        self.run_inbox(items=items, source=source)
        self.assertEqual(len(self.sent), 1)
        self.assertEqual([m['outcome'] for m in self.marked], ['done', 'done'],
                         'Already completed identical work is escalated as an idempotency hold')


class Grants(Case):
    def test_N25_nonzero_or_wrong_recipient_output_cannot_confirm_grant(self):
        for result in (SimpleNamespace(returncode=1, stdout='GRANTED: ada@example.com', stderr='failed'),
                       SimpleNamespace(returncode=0, stdout='GRANTED: other@example.com', stderr='')):
            with self.subTest(result=result):
                j = self.new_journal()
                replies = iter([SimpleNamespace(returncode=0, stdout='NONE: ada@example.com', stderr=''), result,
                                SimpleNamespace(returncode=0, stdout='NONE: ada@example.com', stderr='')])
                ok, line = grant.grant(j, 'sideshift:U1', 'ada@example.com', 'note', lambda *a, **kw: next(replies))
                self.assertFalse(ok, line)

    def test_N25_grant_timeout_checks_before_returning(self):
        import subprocess
        calls = []
        def runner(args, **kw):
            calls.append(args[1])
            if args[1] == 'grant':
                raise subprocess.TimeoutExpired(args, 60)
            return SimpleNamespace(returncode=0, stdout='NONE: ada@example.com', stderr='')
        _, error = self.no_crash(lambda: grant.grant(self.j, 'sideshift:U1', 'ada@example.com', 'note', runner))
        self.assertEqual(calls, ['check', 'grant', 'check'], str(error))

    def test_N26_overlapping_grants_have_one_owner(self):
        calls = []
        nested = [False]
        def runner(args, **kw):
            calls.append(args[1])
            if args[1] == 'grant':
                if not nested[0]:
                    nested[0] = True
                    grant.grant(self.j, 'sideshift:U1', 'ada@example.com', 'overlapping worker', runner)
                return SimpleNamespace(returncode=0, stdout='GRANTED: ada@example.com', stderr='')
            return SimpleNamespace(returncode=0, stdout='NONE: ada@example.com', stderr='')
        grant.grant(self.j, 'sideshift:U1', 'ada@example.com', 'worker one', runner)
        self.assertEqual(calls.count('grant'), 1, 'Both workers check NONE before either has a receipt; no durable grant intent or lock')
