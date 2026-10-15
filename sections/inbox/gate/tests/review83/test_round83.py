import unittest
"""Required behavior at Flow -> Gate -> ContactsMCP's real send boundary.

Only remote responses, the review verdict and clocks are faked. No network.
Run: python3 -m unittest discover -s out/tests -t .
"""
import json
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from gate import policy
from gate.contacts import ContactsMCP
from gate.dispatch import Gate
from gate.live import SideShiftLive
from gate.tests.review3.support import Case, NOW, flow


class LinkedAccountDelivery(Case):
    def setup_system(self, option='a', reparent=False, distinct=False):
        self.j = self.new_journal(self.root / 'shared.db')
        self.clock, self.elapsed = NOW, 0
        self.deliveries = []
        clock = patch('gate.journal.datetime')
        clock.start().now.side_effect = lambda *args: self.clock
        self.addCleanup(clock.stop)
        monotonic = patch('gate.dispatch.time.monotonic', side_effect=lambda: self.elapsed)
        monotonic.start()
        self.addCleanup(monotonic.stop)
        self.persons = {'U1': 'person1', 'U2': 'person2' if distinct else 'person1'}
        self.handles = {'person1': ['U1'] if distinct else ['U1', 'U2'],
                        'person2': ['U2']}
        self.rows = {}
        self.contracts = {}
        for uid in ('U1', 'U2'):
            cid = 'C' + uid[-1]
            self.contracts[uid] = self.contract(id=cid, contractorId=uid, status='active')
            self.rows[uid] = [self.raw('invite' + uid[-1],
                'https://app.sideshift.app/campaign-invite/' + cid,
                NOW - timedelta(hours=7))]
        scheduled = {'contract-reminder-1', 'contract-reminder-2',
                     'warmup-guide', 'ask-app-email'}
        self.types = {k: replace(t, mode='draft') if option == 'b' or
                      (option == 'c' and k not in scheduled) else t
                      for k, t in policy.load().items()}
        self.workers = {uid: self.worker(uid) for uid in ('U1', 'U2')}
        if reparent:
            # Real preflight records the old membership, before Contacts moves U2.
            self.workers['U1'].sender.preflight(self.action_for('U1'))
            self.persons['U2'] = 'person2'
            self.handles['person1'] = ['U1']
            self.workers['U2'].sender.preflight(self.action_for('U2'))
            self.assertEqual(self.j.component_accounts('sideshift:U1'),
                             {'sideshift:U1', 'sideshift:U2'})

    def raw(self, mid, text, at):
        return dict(id=mid, content=text, createdAt=at.isoformat(),
                    senderUserId=flow.COMPANY)

    def action_for(self, uid, kind='warmup-guide'):
        return self.action(message_type=kind, creator_key='sideshift:' + uid,
            person_id=self.persons[uid], source_chat_id='chat' + uid[-1],
            conversation_id='route' + uid[-1], occurrence='C' + uid[-1],
            fields={'First': 'Ada'} if kind == 'warmup-guide' else {},
            contract=dict(self.contracts[uid]))

    def worker(self, uid):
        journal = self.new_journal(self.root / 'shared.db')

        def pages(path, **kwargs):
            if path == '/conversations':
                return [dict(id='chat' + uid[-1], members=[flow.COMPANY, uid])]
            self.assertEqual(path, '/support-channels/chat' + uid[-1] + '/messages')
            return [dict(row) for row in self.rows[uid]]

        live = SideShiftLive(SimpleNamespace(pages=pages), flow.COMPANY,
                             on_notice=journal.remember_notice)
        outer = self

        class Sender(ContactsMCP):
            def __init__(inner):
                inner.live = live
                inner.link_person = journal.link_person
                inner.restricted = journal.restricted
                inner.person_restricted = journal.person_restricted

            def _post(inner, body):
                tool, args = body['params']['name'], body['params']['arguments']
                pid = outer.persons[uid]
                if tool == 'get_conversation':
                    result = dict(id='route' + uid[-1], channel='sideshift',
                        external_id='sideshift:chat' + uid[-1], participants=[
                            dict(value_normalized=uid, person_id=pid)])
                elif tool == 'get_person':
                    outer.assertEqual(args['person_id'], pid)
                    result = dict(person=dict(id=pid, tags=[]), handles=[
                        dict(channel='sideshift', value_normalized=u, person_id=pid)
                        for u in outer.handles[pid]])
                elif tool == 'send_message':
                    outer.deliveries.append(dict(args))
                    result = dict(status='sent', id='out' + str(len(outer.deliveries)))
                else:
                    raise AssertionError(tool)
                return SimpleNamespace(text=json.dumps(dict(jsonrpc='2.0', id=1,
                    result=dict(content=[dict(type='text', text=json.dumps(result))]))))

        sender = Sender()
        gate = Gate(self.types, live, lambda *args: ('SEND', 'offline review', []),
            sender, journal, now=lambda: self.clock, paused_file=self.paused,
            contract_reader=lambda cid: dict(self.contracts[uid]),
            applications_reader=lambda who: [])
        client = SimpleNamespace(pages=lambda *a, **kw: [dict(self.contracts[uid])])
        job = flow.Flow(client, live, gate, journal,
            lambda chat: ('route' + uid[-1], self.persons[uid]),
            now=lambda: self.clock,
            read_client=SimpleNamespace(pages=lambda *a, **kw: []))
        return SimpleNamespace(gate=gate, job=job, live=live, sender=sender, journal=journal)

    def run_job(self, uid):
        report = self.workers[uid].job.run()
        self.assertFalse(any('error ' in line for line in report), report)
        return report

    def manual_delivery(self, kind):
        text = policy.render(self.types[kind], {'First': 'Ada'} if kind == 'warmup-guide' else {})
        self.rows['U1'].append(self.raw('captain-copy', text, NOW - timedelta(hours=4)))
        # A real live read observes a direct SideShift delivery, without a Gate send receipt.
        self.workers['U1'].sender.preflight(self.action_for('U1', kind))
        self.workers['U1'].live.read('chat1', ['U1'])
        self.assertTrue(self.j.flags('sideshift:U1', 'out-seen'))
        self.assertFalse(self.j.spent('gate:' + kind + ':sideshift:U1'))
        self.assertEqual(self.j.component_accounts('sideshift:U1'),
                         {'sideshift:U1', 'sideshift:U2'})
        # A fresh worker must retain the observed delivery after a restart/redaction.
        self.rows['U1'].pop()
        self.workers['U2'] = self.worker('U2')
        return text

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_CS01_observed_manual_guide_must_advance_other_account_to_email(self):
        self.setup_system()
        manual = self.manual_delivery('warmup-guide')
        report = self.run_job('U2')
        self.assertEqual([d['reason'].split(':', 1)[0] for d in self.deliveries],
                         ['ask-app-email'], report)
        self.assertNotIn(manual, [d['text'] for d in self.deliveries])

    def test_CS01_mixed_must_not_repeat_observed_manual_email_request(self):
        self.setup_system(option='c')
        manual = self.manual_delivery('ask-app-email')
        self.rows['U2'].append(self.raw('existing-guide',
            'Warm-up guide: https://docs.google.com/document/d/' + flow.WARMUP_DOC + '/edit',
            NOW - timedelta(hours=5)))
        report = self.run_job('U2')
        self.assertNotIn(manual, [d['text'] for d in self.deliveries], report)

    def overlap(self, option='a', reparent=True, distinct=False):
        self.setup_system(option=option, reparent=reparent, distinct=distinct)

        def first_review(*args):
            # Worker 1 has passed the only cross-account spent check. Its slow
            # review overlaps a complete send by worker 2 on a separate connection.
            self.second_report = self.run_job('U2')
            if distinct:
                self.assertEqual(len(self.deliveries), 1, self.second_report)
                self.assertEqual(self.j.delivery('gate:warmup-guide:sideshift:U2'), 'sent')
            elif reparent:   # adapted 2026-10-15 (CS02 fix): the per-human lock now serialises the second worker
                self.assertIn('being handled', str(self.second_report))
            # Twenty seconds elapse AFTER that confirmed delivery. Every final
            # contract/chat/Contacts read is then fresh, fast and unchanged.
            self.elapsed += 20
            self.clock += timedelta(seconds=20)
            return 'SEND', 'offline review', []

        self.workers['U1'].gate.reviewer = first_review
        report = self.run_job('U1')
        if len(self.deliveries) == 2:
            self.assertEqual(self.deliveries[0]['text'], self.deliveries[1]['text'])
            self.assertNotEqual(self.deliveries[0]['idempotency_key'],
                                self.deliveries[1]['idempotency_key'])
        return report

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_CS02_historical_person_component_must_serialize_auto_workers(self):
        report = self.overlap()
        self.assertEqual(len(self.deliveries), 1, report)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_CS02_historical_person_component_must_serialize_mixed_workers(self):
        report = self.overlap(option='c')
        self.assertEqual(len(self.deliveries), 1, report)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_one_current_person_lock_serializes_workers(self):
        report = self.overlap(reparent=False)
        self.assertEqual(len(self.deliveries), 1, report)
        self.assertIn('being handled', str(self.second_report))

    def test_control_unrelated_people_may_both_receive_guide(self):
        report = self.overlap(reparent=False, distinct=True)
        self.assertEqual(len(self.deliveries), 2, report)

    def test_control_drafts_contain_observed_manual_duplicate(self):
        self.setup_system(option='b')
        self.manual_delivery('warmup-guide')
        report = self.run_job('U2')
        self.assertEqual(self.deliveries, [], report)

    def test_control_drafts_have_no_overlap_delivery(self):
        report = self.overlap(option='b')
        self.assertEqual(self.deliveries, [], report)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_observed_manual_guide_advances_same_account(self):
        self.setup_system()
        self.manual_delivery('warmup-guide')
        report = self.run_job('U1')
        self.assertEqual([d['reason'].split(':', 1)[0] for d in self.deliveries],
                         ['ask-app-email'], report)

    @unittest.skip('superseded 2026-10-15 (review CU01-CU03): a creator with several linked SideShift accounts is now held entirely for the captain (no sends, grants or withdrawal); see gate/tests/test_several_accounts.py')

    def test_control_observed_manual_email_suppresses_same_account(self):
        self.setup_system()
        self.manual_delivery('ask-app-email')
        decision = self.workers['U1'].gate.run(self.action_for('U1', 'ask-app-email'))
        self.assertEqual(self.deliveries, [], str(decision))
        self.assertIn('already', str(decision.reasons))
