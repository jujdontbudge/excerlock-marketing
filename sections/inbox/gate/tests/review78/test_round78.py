import unittest
"""Offline required-behavior assertions at the real send_message boundary.

Only remote records, the clock and the model verdict are faked. The captain's
record.py command, SideShiftLive, Gate, ContactsMCP and SQLite remain real.
Run: python3 -m unittest discover -s out/tests -t .
"""
import sys
from contextlib import ExitStack, redirect_stdout
from dataclasses import replace
from datetime import timedelta
from io import StringIO
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from gate.tests.review3.support import Case, NOW, flow
from gate.tests.review7.test_round7 import CheckedSender
from gate.tests.review35 import test_round35 as fixtures
import record


class CanonicalPersonRestriction(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def run_record(self, command, state):
        def pages(path, **kwargs):
            if path == '/conversations':
                return [dict(id='chat1', members=[flow.COMPANY, 'U1'],
                             participants=[dict(id='U1', name='Ada Example')])]
            self.assertEqual(path, '/contracts')
            return []
        client_module = ModuleType('client')
        client_module.Client = lambda *args: SimpleNamespace(pages=pages)
        dotenv = ModuleType('dotenv')
        dotenv.load_dotenv = lambda *args: None
        with ExitStack() as stack:
            stack.enter_context(patch.dict(sys.modules,
                {'client': client_module, 'dotenv': dotenv}))
            stack.enter_context(patch.dict('os.environ',
                {'SIDESHIFT_CONTRACTS_KEY': 'offline'}))
            stack.enter_context(patch.object(record, 'Journal', return_value=self.j))
            stack.enter_context(patch.object(sys, 'argv',
                ['record.py', command, 'U1', state]))
            output = stack.enter_context(redirect_stdout(StringIO()))
            record.main()
        return output.getvalue()

    def exercise(self, *, option='a', alias=True, same_person=True,
                 canonical_tag=False, enabled=True):
        self.setup_flow()
        # Use the documented captain command, not a hand-written test flag.
        self.assertIn('do-not-contact on', self.run_record('dnc', 'on'))
        self.assertTrue(self.j.restricted('sideshift:U1'))
        if not enabled:
            self.clock += timedelta(seconds=1)
            self.assertIn('do-not-contact off', self.run_record('dnc', 'off'))
            self.assertFalse(self.j.restricted('sideshift:U1'))

        # Contacts already knows that these two SideShift handles belong to
        # ONE canonical person. Each source user has one unambiguous chat.
        uid = 'U2' if alias else 'U1'
        person_id = 'person1' if same_person else 'person2'
        people = {
            'person1': ['U1', 'U2'] if same_person else ['U1'],
            'person2': ['U2'],
        }
        self.current.update(id='C2' if alias else 'C1', contractorId=uid)
        cid = self.current['id']
        self.rows[:] = [self.raw('invite-target',
            f'https://app.sideshift.app/campaign-invite/{cid}',
            NOW - timedelta(hours=7))]

        def pages(path, **kwargs):
            if path == '/conversations':
                return [dict(id=f'chat{i}', members=[flow.COMPANY, f'U{i}'],
                             participants=[dict(id=f'U{i}', name='Ada Example')])
                        for i in (1, 2)]
            self.assertEqual(path, f'/support-channels/chat{uid[-1]}/messages')
            return [dict(row) for row in self.rows]
        self.source.client.pages = pages

        outer = self

        class Sender(CheckedSender):
            def call(inner, tool, args):
                if tool == 'get_conversation':
                    return dict(id=args['conversation_id'], channel='sideshift',
                                external_id=f'sideshift:chat{uid[-1]}',
                                participants=[dict(value_normalized=uid,
                                                   person_id=person_id)])
                if tool == 'get_person':
                    outer.assertEqual(args['person_id'], person_id)
                    return dict(person=dict(id=person_id,
                                tags=['do-not-contact'] if canonical_tag else []),
                                handles=[dict(id=f'handle-{u}', person_id=person_id,
                                              channel='sideshift', value=u,
                                              value_normalized=u)
                                         for u in people[person_id]])
                if tool == 'send_message':
                    inner.delivered.append(args)
                    return dict(status='sent', id='out-target')
                raise AssertionError(tool)

        self.sender = Sender(self.source)
        self.g.sender = self.sender
        self.job.routes = lambda chat: (f'route{uid[-1]}', person_id)
        scheduled = {'contract-reminder-1', 'contract-reminder-2',
                     'warmup-guide', 'ask-app-email'}
        self.g.types = {k: replace(t, mode='draft') if option == 'b' or
                        (option == 'c' and k not in scheduled) else t
                        for k, t in self.g.types.items()}
        # The DNC decision and the identity association are stable well beyond
        # the accepted ten-second window. No captain send approval exists.
        self.clock = NOW + timedelta(minutes=15)
        report = self.job.run()
        self.assertFalse(any('error ' in line for line in report), report)
        if self.sender.delivered:
            self.assertEqual(self.sender.delivered[0]['person_id'], person_id)
            self.assertEqual(self.sender.delivered[0]['text'],
                self.g.types['contract-reminder-1'].text.replace('{First}', 'Ada'))
        return report

    def test_CN01_auto_must_respect_dnc_on_another_handle_of_same_person(self):
        report = self.exercise()
        self.assertEqual(self.sender.delivered, [], report)

    def test_CN01_mixed_must_respect_dnc_on_another_handle_of_same_person(self):
        report = self.exercise(option='c')
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_same_source_user_is_restricted(self):
        report = self.exercise(alias=False)
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('do-not-contact' in line for line in report), report)

    def test_control_canonical_contacts_tag_blocks_alias(self):
        report = self.exercise(canonical_tag=True)
        self.assertEqual(self.sender.delivered, [], report)

    def test_control_drafts_contain_alias_send(self):
        report = self.exercise(option='b')
        self.assertEqual(self.sender.delivered, [], report)
        # adapted 2026-10-15 (CN01 fix): do-not-contact now holds before the draft stage; either contains it
        self.assertTrue(any('draft mode' in line or 'do-not-contact' in line for line in report), report)

    def test_control_another_person_may_receive_due_reminder(self):
        report = self.exercise(same_person=False)
        self.assertEqual(len(self.sender.delivered), 1, report)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_explicitly_released_restriction_allows_send(self):
        report = self.exercise(enabled=False)
        self.assertEqual(len(self.sender.delivered), 1, report)
