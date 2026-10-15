"""Required safety assertions: fail against the reviewed source, entirely offline.

Run: python3 -m unittest discover -s out/tests -t .
Real production entry points, SideShiftLive, Gate, Flow, ContactsMCP boundary and
file-backed SQLite. Only remote responses, clocks and reviewer verdict are faked.
"""
import json
import sys
import types
from contextlib import ExitStack, redirect_stdout
from dataclasses import replace
from datetime import timedelta
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from gate.live import SideShiftLive
from gate.tests.review4.support import NOW, flow, policy, propose
from gate.tests.review21.test_round21 import (
    ReviewCase, clean_source, raw_invite, raw_request,
)
import send


class EntryPointCase(ReviewCase):
    def offline_modules(self, stack, factory):
        client, dotenv = types.ModuleType('client'), types.ModuleType('dotenv')
        client.Client, dotenv.load_dotenv = factory, lambda *a, **kw: None
        stack.enter_context(patch.dict(sys.modules, {'client': client, 'dotenv': dotenv}))
        stack.enter_context(patch.dict('os.environ', {
            'SIDESHIFT_CONTRACTS_KEY': 'offline-contracts',
            'SIDESHIFT_READ_KEY': 'offline-read',
            'SIDESHIFT_CONTRACTS_WRITE_KEY': '',
        }))
        stack.enter_context(redirect_stdout(StringIO()))


class BeforeGateChatRead(EntryPointCase):
    def run_send_until_page_wait(self, concurrent=False):
        clock, consumed, writes, reports = [1000.0], [], [], []
        row = raw_invite(hours=35 + 59 / 60 if concurrent else 10)
        redacted = clean_source({'U1': row})
        now = lambda: NOW + timedelta(seconds=clock[0] - 1000.0)

        class ChatClient:
            def pages(inner, path, **kw):
                if path == '/conversations':
                    yield dict(id='chat1', members=[flow.COMPANY, 'U1'],
                               participants=[dict(id='U1', name='Ada Example')])
                    return
                self.assertEqual(path, '/support-channels/chat1/messages')
                yield row
                consumed.append('notice1')
                yield raw_request()
                # send.main's own invite-generation read, BEFORE Gate construction.
                clock[0] += 120.0
                if concurrent:
                    reports.extend(self.concurrent_withdrawal(redacted, 1, now, writes))
                raise KeyboardInterrupt('stopped while waiting for chat page 2')

        chats = ChatClient()
        contracts = SimpleNamespace(pages=lambda *a, **kw: [self.contract_for()],
                                    request=lambda *a, **kw: {'data': self.contract_for()})
        factory = lambda key=None: chats if key is None else contracts
        with ExitStack() as stack:
            self.offline_modules(stack, factory)
            stack.enter_context(patch.object(sys, 'argv', [
                'send.py', '--creator', 'U1', '--type', 'ask-app-email', '--order', 'send it',
            ]))
            stack.enter_context(patch.object(send, 'Journal', return_value=self.j))
            stack.enter_context(patch.object(flow, 'contacts_routes',
                                            return_value=lambda chat: ('route1', 'person1')))
            stack.enter_context(patch('gate.contacts.ContactsMCP', return_value=SimpleNamespace()))
            stack.enter_context(patch('time.monotonic', side_effect=lambda: clock[0]))
            with self.assertRaises(KeyboardInterrupt):
                send.main()
        self.assertEqual(consumed, ['notice1'])
        self.assertEqual(clock[0], 1120.0)
        return redacted, writes, reports

    def test_AJ01_pre_gate_notice_survives_interruption_before_later_automatic_reminder(self):
        source, _, _ = self.run_send_until_page_wait()
        self.later_reminder(source)

    def test_AJ01_pre_gate_notice_stops_concurrent_automatic_withdrawal(self):
        _, writes, reports = self.run_send_until_page_wait(concurrent=True)
        self.assertEqual(writes, [],
                         f'send.main consumed signing 120s before a concurrent withdrawal: {reports}')


class UnobservedContractList(EntryPointCase):
    def run_inbox_until_page_wait(self, concurrent=False):
        clock, consumed, writes, reports = [1000.0], [], [], []
        source = clean_source({'U1': raw_invite(hours=35 + 59 / 60 if concurrent else 10)})
        now = lambda: NOW + timedelta(seconds=clock[0] - 1000.0)
        # Even an escalation in an all-draft inbox enumerates the campaign's contracts.
        inbox = [dict(id='in1', channel='email', conversation_id='email-route', text='Needs a human')]

        class Contracts:
            def pages(inner, path, **kw):
                self.assertEqual(path, '/contracts')
                consumed.append(('C1', 'active'))
                yield self.contract_for() | {'status': 'active'}
                clock[0] += 120.0
                if concurrent:
                    # Status is now pending and notices/requests have been redacted.
                    reports.extend(self.concurrent_withdrawal(source, 1, now, writes))
                raise KeyboardInterrupt('stopped while waiting for contract page 2')

        class Contacts:
            def call(inner, tool, args):
                if tool == 'list_inbox':
                    return {'items': inbox}
                if tool == 'claim_inbox':
                    return {'claim_token': 'ours', 'message_ids': ['in1']}
                raise AssertionError(tool)

        (self.root / '.claude.json').write_text(json.dumps({
            'mcpServers': {'contacts': {'url': 'offline://fixture'}},
        }))
        drafts = {key: replace(t, mode='draft') for key, t in policy.load().items()}
        with ExitStack() as stack:
            self.offline_modules(stack, lambda key=None: Contracts())
            stack.enter_context(patch.object(sys, 'argv', ['propose.py']))
            stack.enter_context(patch.object(propose, 'HERE', self.root))
            stack.enter_context(patch('pathlib.Path.home', return_value=self.root))
            stack.enter_context(patch.object(propose, 'Journal', return_value=self.j))
            stack.enter_context(patch.object(propose, 'SideShiftLive', return_value=source))
            stack.enter_context(patch.object(policy, 'load', return_value=drafts))
            stack.enter_context(patch.object(propose, 'ask_claude', return_value=json.dumps([
                {'message_id': 'in1', 'action': 'escalate', 'summary': 'Needs captain'},
            ])))
            stack.enter_context(patch('gate.contacts.ContactsMCP', return_value=Contacts()))
            stack.enter_context(patch('time.monotonic', side_effect=lambda: clock[0]))
            with self.assertRaises(KeyboardInterrupt):
                propose.main()
        self.assertEqual(consumed, [('C1', 'active')])
        self.assertEqual(clock[0], 1120.0)
        return source, writes, reports

    def test_AJ02_consumed_active_contract_survives_failed_listing_until_later_reminder(self):
        source, _, _ = self.run_inbox_until_page_wait()
        self.later_reminder(source)

    def test_AJ02_draft_inbox_active_contract_stops_concurrent_automatic_withdrawal(self):
        _, writes, reports = self.run_inbox_until_page_wait(concurrent=True)
        self.assertEqual(writes, [],
                         f'All-draft inbox consumed active status 120s earlier, yet withdrawal ran: {reports}')


class ReminderSchedule(EntryPointCase):
    def assert_inbox_cannot_send_early_reminder(self, message_type, hours):
        class Client:
            def pages(inner, path, **kw):
                if path == '/conversations':
                    return [dict(id='chat1', members=[flow.COMPANY, 'U1'])]
                return [raw_invite(hours=hours), dict(
                    id='source-in1', senderUserId='U1', content='Thanks',
                    createdAt=(NOW - timedelta(minutes=1)).isoformat())]

        source = SideShiftLive(Client(), flow.COMPANY)
        gate, sender = self.configured(source, self.contract_for())
        detail = dict(id='route1', channel='sideshift', external_id='sideshift:chat1',
                      participants=[dict(value_normalized='U1', person_id='person1',
                                         profile={'display_name': 'Ada'})],
                      messages=[dict(id='in1', direction='in', text='Thanks')])
        outcome, note = propose.handle(
            dict(id='in1', channel='sideshift', conversation_id='route1', text='Thanks',
                 external_id='sideshift:default:chat1:source-in1'),
            dict(action='template', message_type=message_type),
            SimpleNamespace(call=lambda tool, args: detail), policy.load(),
            [self.contract_for()], self.j, gate, False)
        self.assertEqual(sender.delivered, [],
                         f'Inbox bypasses the {6 if message_type.endswith("1") else 12}h '
                         f'threshold at invite age {hours}h: {outcome}: {note}')

    def test_AJ03_inbox_cannot_send_reminder_1_before_six_hours(self):
        self.assert_inbox_cannot_send_early_reminder('contract-reminder-1', 1)

    def test_AJ03_inbox_cannot_send_reminder_2_before_twelve_hours(self):
        self.assert_inbox_cannot_send_early_reminder('contract-reminder-2', 7)
