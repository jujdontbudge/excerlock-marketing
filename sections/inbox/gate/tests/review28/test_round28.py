from dataclasses import replace
"""Offline regressions: intentionally fail on the reviewed snapshot.

Run: python3 -m unittest discover -s out/tests -t .
The proposer launch is captured, never executed. The invitation case uses real
Gate, SideShiftLive, ContactsMCP preflight/send and a private SQLite journal.
"""
import fnmatch
import shlex
from types import SimpleNamespace
from unittest.mock import patch

from gate import policy
from gate.tests.review21.test_round21 import ReviewCase, clean_source, raw_invite
from gate.tests.review4.support import propose


def option_values(argv, option):
    """Claude's variadic comma/space-separated tool-list options."""
    values = []
    for index, arg in enumerate(argv):
        if arg == option:
            for value in argv[index + 1:]:
                if value.startswith('--'):
                    break
                values.extend(shlex.split(value.replace(',', ' ')))
    return values


class ProposerCapabilities(ReviewCase):
    def launch(self):
        launches = []

        def run(argv, **kwargs):
            launches.append(argv)
            return SimpleNamespace(returncode=0, stdout='[]', stderr='')

        with patch.object(propose.subprocess, 'run', side_effect=run):
            self.assertEqual(propose.ask_claude([], policy.load()), '[]')
        self.assertEqual(len(launches), 1)
        return launches[0]

    def test_AP01_read_only_proposer_must_remove_mutating_builtin_tools(self):
        argv = self.launch()
        # Local `claude --help`: --tools selects the available built-ins;
        # --allowedTools only allows permission rules. With inherited
        # bypassPermissions, listing Read/Glob/Grep does not disable Bash/Write.
        available = (set(option_values(argv, '--tools')) if '--tools' in argv
                     else {'Read', 'Glob', 'Grep', 'Bash', 'Edit', 'Write', 'NotebookEdit'})
        if 'default' in available:
            available |= {'Bash', 'Edit', 'Write', 'NotebookEdit'}
        denied = option_values(argv, '--disallowedTools')
        dangerous = {tool for tool in available & {'Bash', 'Edit', 'Write', 'NotebookEdit'}
                     if not any(fnmatch.fnmatchcase(tool, pattern) for pattern in denied)}
        self.assertEqual(dangerous, set(),
                         'The read-only proposer retains mutating built-ins under inherited bypassPermissions')

    def test_AP01_full_contacts_server_must_not_expose_send_to_proposer(self):
        argv = self.launch()
        # propose.main writes the full contacts server config into the runtime
        # config. --strict-mcp-config limits SERVERS, not that server's tools.
        # No real model, MCP server, message or network request is used here.
        denied = option_values(argv, '--disallowedTools')
        self.assertTrue(any(fnmatch.fnmatchcase('mcp__contacts__send_message', rule)
                            for rule in denied),
                        'The full contacts server send_message tool is not denied; the allowedTools list cannot '
                        'enforce read-only access under bypassPermissions')


class InvitationFields(ReviewCase):
    def test_AP02_valid_contract_invite_proposal_must_render_and_reach_gate_send(self):
        source = clean_source({'U1': raw_invite(hours=10)})
        contract = self.contract_for()
        gate, sender = self.configured(source, contract)
        gate.types = {**gate.types, 'contract-invite': replace(gate.types['contract-invite'], mode='auto', source=None)}   # adapted 2026-10-15: on here, not re-read from the fixture file
        detail = dict(id='route1', channel='sideshift', external_id='sideshift:chat1',
                      participants=[dict(value_normalized='U1', person_id='person1',
                                         profile={'display_name': 'Ada Example'})], messages=[])
        contacts = SimpleNamespace(call=lambda tool, args: detail)
        outcome, note = propose.handle(
            dict(id='in1', external_id='sideshift:in1', channel='sideshift',
                 conversation_id='route1', text='Yes, please send the signing instructions.'),
            dict(action='template', message_type='contract-invite'), contacts,
            {**policy.load(), 'contract-invite': replace(policy.load()['contract-invite'], mode='auto')},   # adapted 2026-10-15: off in the fixture copy
            [contract], self.j, gate, False)
        # adapted 2026-10-15 (review CC01): its source message isn't in this chat, so after the send the item goes to
        # the captain instead of 'done'; the point here is that the invitation renders and is delivered
        self.assertTrue(outcome == 'done' or (outcome == 'escalated' and 'gate sent contract-invite' in note), note)
        self.assertEqual(len(sender.delivered), 1)
