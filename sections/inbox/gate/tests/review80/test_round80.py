import unittest
"""Offline assertions at the real send_message and Premium grant boundaries.

Only remote responses, the model verdict, entitlement CLI and clock are faked.
Run: python3 -m unittest discover -s out/tests -t .
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate.tests.review3.support import Case, NOW, flow, grant
from gate.contacts import ContactsMCP
from gate.dispatch import Gate
from gate.live import SideShiftLive
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review78 import test_round78 as record_fixture


class RestrictionSurvivesHandleRemoval(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw
    run_record = record_fixture.CanonicalPersonRestriction.run_record

    def exercise(self, *, option='a', premium=False, remove=True,
                 clear=False, same_person=True, restart=False):
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
        self.person_id = 'person1' if same_person else 'person2'
        # Entirely readable, canonical records. No malformed fields or schema
        # alternatives. U1 is initially a linked account of this same person.
        self.handles = [dict(id=f'h{uid[-1]}', person_id=self.person_id,
                             channel='sideshift', value=uid,
                             value_normalized=uid)
                        for uid in (['U1', 'U2'] if same_person else ['U2'])]
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
                            value_normalized='U2', person_id=outer.person_id)])
                elif tool == 'get_person':
                    result = dict(person=dict(id=outer.person_id, tags=[]),
                                  handles=[dict(h) for h in outer.handles])
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
        self.job.routes = lambda chat: ('route2', self.person_id)
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

        def run():
            if premium:
                return self.g.run(self.action(message_type='app-access',
                    source_chat_id='chat2', conversation_id='route2',
                    person_id=self.person_id, creator_key='sideshift:U2',
                    occurrence='C2', fields={'email': 'ada@example.com'},
                    contract=dict(self.current)))
            report = self.job.run()
            self.assertFalse(any('error ' in line for line in report), report)
            return report

        # The real gate has positively learned this person's restriction and
        # held an actual action before any identity maintenance happens.
        self.clock = NOW + timedelta(minutes=15)
        if same_person:
            first = run()
            self.assertEqual(self.sender.delivered, [], str(first))
            self.assertEqual(self.commands, [], str(first))
            self.assertIn('do-not-contact', str(first))
        if clear:
            self.clock += timedelta(seconds=1)
            self.assertIn('do-not-contact off', self.run_record('dnc', 'off'))
        if remove:
            self.handles[:] = [h for h in self.handles
                               if h['value_normalized'] != 'U1']
        if not clear:
            self.assertTrue(self.j.restricted('sideshift:U1'))
        if restart:
            # A fresh SQLite connection and Gate, as on the next scheduled job.
            old = self.g
            self.j = self.new_journal(self.root / 'gate.db')
            self.source.on_notice = self.j.remember_notice
            self.g = Gate(old.types, self.source, old.reviewer, self.sender,
                self.j, now=lambda: self.clock, paused_file=self.paused,
                contract_reader=old.contract_reader, granter=old.granter,
                applications_reader=old.applications_reader)
            self.job.gate, self.job.journal = self.g, self.j
        # Same canonical person, route, U2, contract and text. The only change
        # is removal of the old account from Contacts. No captain clears DNC.
        # Every remote response has been stable for fifteen minutes.
        self.clock += timedelta(minutes=15)
        return run()

    def test_CP01_auto_removal_must_not_clear_known_person_restriction(self):
        report = self.exercise()
        self.assertEqual(self.sender.delivered, [], str(report))

    def test_CP01_mixed_removal_must_not_clear_known_person_restriction(self):
        report = self.exercise(option='c')
        self.assertEqual(self.sender.delivered, [], str(report))

    def test_CP01_removal_must_not_authorize_premium_grant(self):
        result = self.exercise(premium=True)
        self.assertEqual([c for c in self.commands if c[1] == 'grant'], [], str(result))

    def test_CP01_known_restriction_must_survive_next_job(self):
        report = self.exercise(restart=True)
        self.assertEqual(self.sender.delivered, [], str(report))

    def test_control_retained_restricted_handle_still_holds(self):
        report = self.exercise(remove=False)
        self.assertEqual(self.sender.delivered, [], str(report))
        self.assertIn('do-not-contact', str(report))

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_captain_can_explicitly_clear_restriction(self):
        report = self.exercise(clear=True, remove=False)
        self.assertFalse(self.j.restricted('sideshift:U1'))
        self.assertEqual(len(self.sender.delivered), 1, str(report))

    def test_control_different_person_is_unrestricted(self):
        report = self.exercise(same_person=False)
        self.assertEqual(len(self.sender.delivered), 1, str(report))

    def test_control_drafts_contain_reminder(self):
        report = self.exercise(option='b')
        self.assertEqual(self.sender.delivered, [], str(report))
        # adapted 2026-10-15 (CP01 fix): the person restriction now holds before the draft stage
        self.assertTrue('draft mode' in str(report) or 'do-not-contact' in str(report), str(report))

    def test_control_mixed_mode_contains_premium(self):
        result = self.exercise(option='c', premium=True)
        self.assertEqual(self.commands, [], str(result))
        self.assertEqual(self.sender.delivered, [], str(result))
        self.assertIn(result.outcome, ('draft', 'held'), str(result))   # adapted 2026-10-15 (CP01 fix)

    def test_control_drafts_contain_premium(self):
        result = self.exercise(option='b', premium=True)
        self.assertEqual(self.commands, [], str(result))
        self.assertEqual(self.sender.delivered, [], str(result))
        self.assertIn(result.outcome, ('draft', 'held'), str(result))   # adapted 2026-10-15 (CP01 fix)
