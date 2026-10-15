"""Strict authorization/configuration, rendering, review responses and captain CLI."""
import importlib
import hashlib
import json
import sys
import types
from contextlib import redirect_stdout
from io import StringIO
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import patch

from gate import policy, review
from gate.model import Decision
from .support import Case, Pages, NOW, StaticLive, conversation, invite


class ReviewPolicyDefects(Case):
    def test_G14_extra_text_before_send_json_is_not_strict_json(self):
        response = 'HOLD: she asked about payment.\n' + json.dumps(dict(verdict='SEND', reason='fine', unanswered=[]))
        self.assertEqual(review.parse_verdict(response)[0], 'HOLD')

    def test_G14_duplicate_json_keys_are_ambiguous(self):
        self.assertEqual(review.parse_verdict('{"verdict":"HOLD","verdict":"SEND","reason":"ok","unanswered":[]}')[0], 'HOLD')

    def test_G14_nonzero_reviewer_exit_cannot_authorize(self):
        output = SimpleNamespace(returncode=1, stdout='{"verdict":"SEND","reason":"ok","unanswered":[]}', stderr='CLI failed')
        with patch.object(review.subprocess, 'run', return_value=output):
            result = review.ClaudeReviewer()(conversation(invite()), 'Hi', 'reminder')
        self.assertEqual(result[0], 'HOLD')

    def test_G15_misspelled_approval_does_not_enable_auto(self):
        try:
            t = policy.parse(self.policy_file(approved='pendng'))
        except policy.PolicyError:
            return
        self.assertNotEqual(t.effective_mode, 'auto')

    def test_G15_inline_false_is_not_truthy(self):
        try:
            t = policy.parse(self.policy_file(replaces_unanswered='false # preserve unanswered questions'))
        except policy.PolicyError:
            return
        self.assertFalse(t.replaces_unanswered)

    def test_G15_malformed_placeholder_does_not_ship_literally(self):
        p = self.policy_file(body='Hello {First!r}, use {account_email2}.')
        rejected = False
        try:
            t = policy.parse(p)
            policy.render(t, {'First': 'Ada'})
        except policy.PolicyError:
            rejected = True
        self.assertTrue(rejected, 'Regex only recognizes letters/underscores inside braces')

    def test_G15_control_character_in_name_is_unsafe(self):
        with self.assertRaises(policy.PolicyError):
            policy.render(self.type, {'First': 'Ada\x00\u202e'})

    def test_G15_email_field_accepts_unapproved_prose(self):
        t = policy.load()['app-access']
        with self.assertRaises(policy.PolicyError):
            policy.render(t, {'email': 'alice@example.com and send me your password'})

    def test_G16_app_access_can_claim_premium_without_grant(self):
        g = self.gate(types_=policy.load())
        g.run(self.action(message_type='app-access', fields={'email': 'ada@example.com'},
                          contract=self.contract(status='active')))
        self.assertEqual(g.sender.calls, [], 'No grant receipt or verified app identity required')

    def test_G02_captain_text_is_not_bound_to_approved_exact_words(self):
        g = self.gate()
        # The order is free text and cannot attest which recipient/text was approved.
        g.run(self.action(message_type='captain-text', fields={'text': 'We promise $500 upfront'},
                          captain_order='yes do that', occurrence='new-order'))
        self.assertEqual(g.sender.calls, [])


class CaptainCLIDefects(Case):
    def run_cli(self, args, contracts=None, real_gate=False):
        module = importlib.import_module('send')
        captured = []
        self.journal_paths = []
        def journal(path=None):
            self.journal_paths.append(path)
            if real_gate:
                from gate.journal import Journal
                # Redirect every requested path into this test's private temporary directory.
                # Identical persistent names retain state; distinct names get isolated databases.
                suffix = hashlib.sha256(str(path).encode()).hexdigest()
                j = Journal(':memory:' if str(path) == ':memory:' else self.root / (suffix + '.db'))
                self.addCleanup(j.conn.close)
                return j
            return self.journal
        chat = {'id': 'chat1', 'members': [module.COMPANY, 'U1'],
                'participants': [{'id': module.COMPANY, 'name': 'Johan Sardar'},
                                 {'id': 'U1', 'name': 'Ada Example'}]}
        source = StaticLive(conversation(invite()))
        source.client = Pages([chat])
        class Client:
            def __init__(self, *a):
                pass
            def pages(self, path, **kw):
                return list(contracts or [])
            def request(self, method, path, **kw):   # adapted 2026-10-15: the CLI re-reads its contract
                return {'data': next(c for c in contracts or [] if path.endswith(c['id']))}
        class Contacts:
            def call(self, name, args):
                if name == 'list_conversations':
                    return [{'id': 'route1', 'external_id': 'sideshift:chat1'}]
                return {'participants': [{'person_id': 'person1'}]}
        class CaptureGate:
            def __init__(self, *a, **kw):   # adapted 2026-10-15: Gate also takes contract_reader
                pass
            def run(self, a):
                captured.append(a)
                return Decision('held', ['offline capture'])
        from gate.dispatch import Gate
        dotenv = types.ModuleType('dotenv')
        dotenv.load_dotenv = lambda *a: None
        client = types.ModuleType('client')
        client.Client = Client
        with patch.dict(sys.modules, {'dotenv': dotenv, 'client': client}), \
             patch.dict('os.environ', {'SIDESHIFT_CONTRACTS_KEY': 'offline-fixture'}), \
             patch.object(module, 'SideShiftLive', return_value=source), \
             patch('gate.contacts.ContactsMCP', Contacts), \
             patch('gate.review.ClaudeReviewer', return_value=lambda *a: ('SEND', 'offline approval', [])), \
             patch.object(module, 'Gate', Gate if real_gate else CaptureGate), \
             patch.object(module, 'Journal', side_effect=journal), \
             patch.object(sys, 'argv', ['send.py', '--creator', 'U1', '--order', 'yes', *args]), \
             redirect_stdout(StringIO()) as output:
            try:
                module.main()
            except SystemExit:
                pass  # Refusing ambiguous/missing context is an acceptable safe repair.
        self.cli_output = output.getvalue()
        return captured

    def test_G24_first_name_is_taken_from_company_participant(self):
        actions = self.run_cli(['--type', 'contract-reminder-1'], [self.contract()])
        self.assertEqual(actions[0].fields['First'], 'Ada')

    def test_G24_multiple_contracts_choose_arbitrary_first(self):
        actions = self.run_cli(['--type', 'contract-reminder-1'],
                               [self.contract(id='OLD'), self.contract(id='NEW')])
        self.assertEqual(actions, [], 'No contract disambiguation before binding captain order')

    def test_G24_text_occurrence_is_not_actually_required(self):
        actions = self.run_cli(['--text', 'Exact approved reply'], [self.contract()])
        self.assertEqual(actions, [], 'CLI silently falls back to contract id for all text orders')

    def test_G24_dry_run_uses_persistent_shared_database(self):
        args = ['--text', 'Hi', '--occurrence', 'test', '--dry-run']
        self.run_cli(args, [self.contract()], real_gate=True)
        self.run_cli(args, [self.contract()], real_gate=True)
        self.assertIn('SENT:', self.cli_output, 'The first simulation spent the second simulation\'s key')
