import unittest
"""Required-behavior assertions at the real send and grant boundaries.

No network: remote responses, the entitlement CLI, clock and review are faked.
The captain command, Flow, SideShiftLive, Gate, ContactsMCP and SQLite are real.
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate.tests.review3.support import Case, NOW, flow, grant
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review78 import test_round78 as record_fixture
from gate.contacts import ContactsMCP
from gate.dispatch import Gate
from gate.live import SideShiftLive


class DurableIdentityRestrictions(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw
    run_record = record_fixture.CanonicalPersonRestriction.run_record

    def exercise(self, transition, *, option='a', premium=False,
                 restart=False, clear=False):
        self.setup_flow()
        self.assertIn('do-not-contact on', self.run_record('dnc', 'on'))
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
        self.person_id = 'person1'
        self.tags = ['do-not-contact'] if transition == 'tag-hold' else []
        self.handles = [dict(id=f'h{uid[-1]}', person_id='person1',
                             channel='sideshift', value=uid,
                             value_normalized=uid) for uid in ('U1', 'U2')]
        if transition == 'unreadable-hold':
            # U1 and U2 are fully readable; another account is unreadable.
            self.handles.append(dict(id='other', channel=None,
                                     value_normalized=None))
        outer = self

        class Sender(ContactsMCP):
            def __init__(inner):
                inner.live, inner.delivered = outer.source, []

            def _post(inner, body):
                tool, args = body['params']['name'], body['params']['arguments']
                if tool == 'get_conversation':
                    result = dict(id='route2', channel='sideshift',
                        external_id='sideshift:chat2', participants=[dict(
                            value_normalized='U2', person_id=outer.person_id)])
                elif tool == 'get_person':
                    outer.assertEqual(args['person_id'], outer.person_id)
                    result = dict(person=dict(id=outer.person_id,
                                             tags=list(outer.tags)),
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

        self.clock = NOW + timedelta(minutes=15)
        first = run()
        self.assertEqual(self.sender.delivered, [], str(first))
        self.assertEqual(self.commands, [], str(first))
        self.assertTrue('do-not-contact' in str(first) or "can't be read" in str(first), str(first))
        self.links_before = self.j.flags('person:person1', 'linked-account')
        if transition == 'reparent':
            self.assertEqual(self.links_before, {'sideshift:U1', 'sideshift:U2'})
        if clear:
            self.clock += timedelta(seconds=1)
            self.assertIn('do-not-contact off', self.run_record('dnc', 'off'))

        # Contacts removes U1. The next read is entirely readable. For the
        # reparent case it also consolidates the remaining U2 under person2.
        # U2's source identity, route, chat, contract and name never change.
        self.handles[:] = [h for h in self.handles if h.get('value_normalized') == 'U2']
        self.tags[:] = []
        if transition == 'reparent':
            self.person_id = 'person2'
            self.handles[0]['person_id'] = self.person_id
        if restart:
            old = self.g
            self.j = self.new_journal(self.root / 'gate.db')
            self.source.on_notice = self.j.remember_notice
            self.g = Gate(old.types, self.source, old.reviewer, self.sender,
                self.j, now=lambda: self.clock, paused_file=self.paused,
                contract_reader=old.contract_reader, granter=old.granter,
                applications_reader=old.applications_reader)
            self.job.gate, self.job.journal = self.g, self.j
        self.assertEqual(self.j.restricted('sideshift:U1'), not clear)
        self.clock += timedelta(minutes=15)
        return run()

    def test_CQ01_reparent_must_not_clear_restriction_auto(self):
        result = self.exercise('reparent')
        self.assertEqual(self.sender.delivered, [], str(result))

    def test_CQ01_reparent_must_not_clear_restriction_mixed(self):
        result = self.exercise('reparent', option='c')
        self.assertEqual(self.sender.delivered, [], str(result))

    def test_CQ01_reparent_must_not_authorize_premium(self):
        result = self.exercise('reparent', premium=True)
        self.assertEqual([c for c in self.commands if c[1] == 'grant'], [], str(result))

    def test_CQ01_reparent_must_hold_after_restart(self):
        result = self.exercise('reparent', restart=True)
        self.assertEqual(self.sender.delivered, [], str(result))

    def test_CQ02_earlier_tag_hold_must_preserve_readable_links(self):
        result = self.exercise('tag-hold')
        self.assertEqual(self.sender.delivered, [], str(result))

    def test_CQ02_earlier_unreadable_hold_must_preserve_readable_links(self):
        result = self.exercise('unreadable-hold', option='c', restart=True)
        self.assertEqual(self.sender.delivered, [], str(result))

    def test_CQ02_earlier_tag_hold_must_not_authorize_premium(self):
        result = self.exercise('tag-hold', premium=True)
        self.assertEqual([c for c in self.commands if c[1] == 'grant'], [], str(result))

    def test_control_drafts_contain_reparent_reminder(self):
        result = self.exercise('reparent', option='b')
        self.assertEqual(self.sender.delivered, [], str(result))
        self.assertTrue('draft' in str(result) or 'do-not-contact' in str(result), str(result))   # adapted (CQ01 fix)

    def test_control_mixed_contains_reparent_premium(self):
        result = self.exercise('reparent', option='c', premium=True)
        self.assertEqual(self.commands, [], str(result))
        self.assertEqual(self.sender.delivered, [], str(result))
        self.assertIn(result.outcome, ('draft', 'held'))   # adapted 2026-10-15 (CQ01/CQ02 fix): held earlier

    def test_control_drafts_contain_earlier_tag_hold_premium(self):
        result = self.exercise('tag-hold', option='b', premium=True)
        self.assertEqual(self.commands, [], str(result))
        self.assertEqual(self.sender.delivered, [], str(result))
        self.assertIn(result.outcome, ('draft', 'held'))   # adapted 2026-10-15 (CQ01/CQ02 fix): held earlier

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_captain_source_clearance_allows_reparent(self):
        result = self.exercise('reparent', clear=True)
        self.assertEqual(len(self.sender.delivered), 1, str(result))
