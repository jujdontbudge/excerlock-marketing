import unittest
"""Offline required-behavior tests; failures reach real send_message/grant boundaries.

Run: python3 -m unittest discover -s out/tests -t .
Only remote responses, the review verdict, entitlement CLI and clock are faked.
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate.contacts import ContactsMCP
from gate.live import SideShiftLive
from gate.tests.review3.support import Case, NOW, flow, grant
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review78 import test_round78 as previous


class UnreadableLinkedAccount(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw
    run_record = previous.CanonicalPersonRestriction.run_record

    def exercise(self, alias, *, option='a', premium=False, wrapped=True):
        self.setup_flow()
        self.assertIn('do-not-contact on', self.run_record('dnc', 'on'))
        self.assertTrue(self.j.restricted('sideshift:U1'))
        self.current.update(id='C2', contractorId='U2',
                            status='active' if premium else 'pending')
        self.rows[:] = [self.raw('invite2',
            'https://app.sideshift.app/campaign-invite/C2',
            NOW - timedelta(hours=7))]
        if premium:
            self.rows.append(dict(id='email', senderUserId='U2',
                createdAt=(NOW - timedelta(hours=1)).isoformat(),
                content='ada@example.com'))

        def pages(path, **kwargs):
            if path == '/conversations':
                return [dict(id='chat2', members=[flow.COMPANY, 'U2'])]
            self.assertEqual(path, '/support-channels/chat2/messages')
            return [dict(row) for row in self.rows]

        self.source = SideShiftLive(SimpleNamespace(pages=pages), flow.COMPANY,
                                    on_notice=self.j.remember_notice)
        outer = self

        class Sender(ContactsMCP):
            def __init__(inner):
                inner.live, inner.delivered = outer.source, []

            def _post(inner, body):
                tool = body['params']['name']
                args = body['params']['arguments']
                if tool == 'get_conversation':
                    result = dict(id='route2', channel='sideshift',
                        external_id='sideshift:chat2', participants=[dict(
                            value_normalized='U2', person_id='person1')])
                elif tool == 'get_person':
                    handles = [dict(id='h2', person_id='person1',
                                    channel='sideshift', value='U2',
                                    value_normalized='U2'), alias]
                    person = dict(id='person1', tags=[])
                    result = (dict(person=person, handles=handles) if wrapped
                              else dict(person, handles=handles))
                elif tool == 'send_message':
                    inner.delivered.append(args)
                    result = dict(status='sent', id='out2')
                else:
                    raise AssertionError(tool)
                return SimpleNamespace(text=json.dumps(dict(jsonrpc='2.0', id=1,
                    result=dict(content=[dict(type='text', text=json.dumps(result))]))))

        self.sender = Sender()
        self.g.sender, self.g.live = self.sender, self.source
        self.job.live = self.source
        self.job.routes = lambda chat: ('route2', 'person1')
        scheduled = {'contract-reminder-1', 'contract-reminder-2',
                     'warmup-guide', 'ask-app-email'}
        self.g.types = {k: replace(t, mode='draft') if option == 'b' or
                        (option == 'c' and k not in scheduled) else t
                        for k, t in self.g.types.items()}
        self.commands = []
        active = [False]

        def runner(argv, **kwargs):
            self.commands.append(argv)
            word = 'ACTIVE' if active[0] else 'NONE'
            if argv[1] == 'grant':
                active[0], word = True, 'GRANTED'
            return SimpleNamespace(returncode=0,
                stdout=f'{word}: ada@example.com', stderr='')

        self.g.granter = lambda a: grant.grant(self.j, a.creator_key,
            a.fields['email'], 'offline review', runner)
        # Stable broken identity evidence, fifteen minutes after DNC; no race
        # or sleep and every final remote read completes in the same instant.
        self.clock = NOW + timedelta(minutes=15)
        if premium:
            return self.g.run(self.action(message_type='app-access',
                source_chat_id='chat2', conversation_id='route2',
                creator_key='sideshift:U2', occurrence='C2',
                fields={'email': 'ada@example.com'}, contract=dict(self.current)))
        report = self.job.run()
        self.assertFalse(any('error ' in line for line in report), report)
        return report

    def bad_alias(self):
        return dict(id='h1', person_id='person1', channel='sideshift',
                    value='U1', value_normalized=None)

    def test_CO01_auto_unknown_alias_id_must_hold_reminder(self):
        report = self.exercise(self.bad_alias())
        self.assertEqual(self.sender.delivered, [], report)

    def test_CO01_mixed_unknown_alias_id_must_hold_reminder(self):
        report = self.exercise(self.bad_alias(), option='c', wrapped=False)
        self.assertEqual(self.sender.delivered, [], report)

    def test_CO01_unreadable_channel_must_hold_reminder(self):
        alias = dict(id='h1', person_id='person1', channel=None,
                     value='U1', value_normalized='U1')
        report = self.exercise(alias)
        self.assertEqual(self.sender.delivered, [], report)

    def test_CO01_unknown_alias_id_must_prevent_premium_grant(self):
        result = self.exercise(self.bad_alias(), premium=True)
        self.assertEqual([c for c in self.commands if c[1] == 'grant'], [], str(result))

    def test_control_readable_restricted_alias_holds(self):
        alias = dict(id='h1', person_id='person1', channel='sideshift',
                     value='U1', value_normalized='U1')
        report = self.exercise(alias)
        self.assertEqual(self.sender.delivered, [], report)
        self.assertTrue(any('do-not-contact' in line for line in report), report)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_unrelated_readable_account_allows_reminder(self):
        alias = dict(id='h3', person_id='person1', channel='sideshift',
                     value='U3', value_normalized='U3')
        report = self.exercise(alias)
        self.assertEqual(len(self.sender.delivered), 1, report)

    def test_control_drafts_contain_unknown_alias_reminder(self):
        report = self.exercise(self.bad_alias(), option='b')
        self.assertEqual(self.sender.delivered, [], report)
        # adapted 2026-10-15 (CO01 fix): the unreadable alias now holds before the draft stage; either contains it
        self.assertTrue(any('draft mode' in line or "can't be read" in line for line in report), report)

    def test_control_mixed_drafts_contain_unknown_alias_premium(self):
        result = self.exercise(self.bad_alias(), option='c', premium=True)
        self.assertEqual(self.commands, [], str(result))
        self.assertEqual(self.sender.delivered, [], str(result))
