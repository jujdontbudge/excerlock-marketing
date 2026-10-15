import unittest
"""Required behavior at the real Flow/Gate/ContactsMCP delivery boundary.

Only service responses, clocks and the model verdict are faked; no network.
Run: python3 -m unittest discover -s out/tests -t .
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate.tests.review3.support import Case, NOW, flow
from gate.tests.review35 import test_round35 as fixtures
from gate.contacts import ContactsMCP
from gate.dispatch import Gate
from gate.live import SideShiftLive


class PersonOnceDelivery(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def exercise(self, *, email=False, option='a', restart=False,
                 same_person=True, same_account=False, reparent=False):
        self.setup_flow()
        self.uid, self.pid = 'U1', 'person1'
        self.current['status'] = 'active'
        self.deliveries = []
        outer = self

        def pages(path, **kwargs):
            if path == '/conversations':
                return [dict(id='chat' + outer.uid[-1],
                    members=[flow.COMPANY, outer.uid])]
            self.assertEqual(path, '/support-channels/chat' + self.uid[-1] + '/messages')
            return [dict(row) for row in self.rows]

        self.source = SideShiftLive(SimpleNamespace(pages=pages), flow.COMPANY,
                                    on_notice=self.j.remember_notice)

        class Sender(ContactsMCP):
            def __init__(inner):
                inner.live = outer.source

            def _post(inner, body):
                tool, args = body['params']['name'], body['params']['arguments']
                if tool == 'get_conversation':
                    result = dict(id='route' + outer.uid[-1], channel='sideshift',
                        external_id='sideshift:chat' + outer.uid[-1],
                        participants=[dict(value_normalized=outer.uid,
                                           person_id=outer.pid)])
                elif tool == 'get_person':
                    # Initially both accounts explicitly belong to ONE person.
                    # The unrelated-person control has one account per person.
                    users = ['U1', 'U2'] if same_person and not reparent else [outer.uid]
                    if reparent and outer.uid == 'U1':
                        users = ['U1', 'U2']
                    result = dict(person=dict(id=outer.pid, tags=[]), handles=[
                        dict(channel='sideshift', value_normalized=u,
                             person_id=outer.pid) for u in users])
                elif tool == 'send_message':
                    outer.deliveries.append(args)
                    result = dict(status='sent', id='out' + str(len(outer.deliveries)))
                else:
                    raise AssertionError(tool)
                return SimpleNamespace(text=json.dumps(dict(jsonrpc='2.0', id=1,
                    result=dict(content=[dict(type='text', text=json.dumps(result))]))))

        self.sender = Sender()
        self.g.live, self.g.sender = self.source, self.sender
        self.job.live = self.source
        self.job.routes = lambda chat: ('route' + self.uid[-1], self.pid)
        scheduled = {'contract-reminder-1', 'contract-reminder-2',
                     'warmup-guide', 'ask-app-email'}
        self.g.types = {k: replace(t, mode='draft') if option == 'b' or
                        (option == 'c' and k not in scheduled) else t
                        for k, t in self.g.types.items()}
        target = 'ask-app-email' if email else 'warmup-guide'

        def history():
            self.rows[:] = [self.raw('invite' + self.uid[-1],
                'https://app.sideshift.app/campaign-invite/' + self.current['id'],
                NOW - timedelta(hours=7))]
            if email:
                self.rows.append(self.raw('guide' + self.uid[-1],
                    'Warm-up guide: https://docs.google.com/document/d/' + flow.WARMUP_DOC + '/edit',
                    NOW - timedelta(hours=5)))

        history()
        first = self.job.run()
        if option != 'b':
            self.assertEqual(len(self.deliveries), 1, first)
            self.assertIn(target + ':', self.deliveries[0]['reason'])
            self.assertEqual(self.j.delivery('gate:' + target + ':sideshift:U1'), 'sent')
        else:
            self.assertEqual(self.deliveries, [], first)
        self.assertEqual(self.j.flags('person:person1', 'linked-account'),
                         {'sideshift:U1', 'sideshift:U2'} if same_person else {'sideshift:U1'})

        if not same_account:
            self.uid = 'U2'
            self.current.update(id='C2', contractorId='U2')
        if not same_person or reparent:
            self.pid = 'person2'
        history()
        self.clock += timedelta(minutes=15)
        if restart:
            old = self.g
            self.j = self.new_journal(self.root / 'gate.db')
            self.source.on_notice = self.j.remember_notice
            self.g = Gate(old.types, self.source, old.reviewer, self.sender,
                self.j, now=lambda: self.clock, paused_file=self.paused,
                contract_reader=old.contract_reader,
                applications_reader=old.applications_reader)
            self.job.gate, self.job.journal = self.g, self.j
        report = self.job.run()
        self.assertFalse(any('error ' in line for line in report), report)
        if len(self.deliveries) == 2:
            self.assertEqual(self.deliveries[0]['text'], self.deliveries[1]['text'])
            self.assertNotEqual(self.deliveries[0]['idempotency_key'],
                                self.deliveries[1]['idempotency_key'])
        return report

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_CR01_auto_guide_must_be_once_for_one_known_person(self):
        result = self.exercise()
        self.assertEqual(len(self.deliveries), 1, result)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_CR01_mixed_guide_must_be_once_for_one_known_person(self):
        result = self.exercise(option='c')
        self.assertEqual(len(self.deliveries), 1, result)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_CR01_email_request_must_be_once_for_one_known_person(self):
        result = self.exercise(email=True)
        self.assertEqual(len(self.deliveries), 1, result)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_CR01_mixed_email_request_must_be_once_after_restart(self):
        result = self.exercise(email=True, option='c', restart=True)
        self.assertEqual(len(self.deliveries), 1, result)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_CR01_person_move_must_preserve_delivered_guide(self):
        result = self.exercise(reparent=True, restart=True)
        self.assertEqual(len(self.deliveries), 1, result)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_same_account_does_not_receive_guide_twice(self):
        result = self.exercise(same_account=True)
        self.assertEqual(len(self.deliveries), 1, result)

    def test_control_distinct_people_may_each_receive_guide(self):
        result = self.exercise(same_person=False)
        self.assertEqual(len(self.deliveries), 2, result)

    def test_control_drafts_contain_alias_guide(self):
        result = self.exercise(option='b')
        self.assertEqual(self.deliveries, [], result)

    def test_control_drafts_contain_alias_email_request(self):
        result = self.exercise(email=True, option='b')
        self.assertEqual(self.deliveries, [], result)
