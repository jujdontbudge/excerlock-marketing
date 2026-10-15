"""Required safety assertions: offline counterexamples against the reviewed source.

Run: python3 -m unittest discover -s out/tests -t .
Real production collectors, CLI entry points, Gate, Flow, SideShiftLive,
ContactsMCP preflight/send and file-backed SQLite; only services/clocks/review faked.
"""
import runpy
import sys
from contextlib import ExitStack
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from gate.tests.review21.test_round21 import ReviewCase, clean_source, raw_invite, raw_request
from gate.tests.review22.test_round22 import EntryPointCase
from gate.tests.review4.support import NOW, flow, policy
import record


class UnreadableApplicationOwner(ReviewCase):
    def unreadable(self):
        # It is a campaign handle request, but its owner cannot be read. It
        # could be U1's: neither collector may certify an empty list for U1.
        return dict(id='request1', programId=flow.CAMPAIGN, creator=None,
                    isJoinRequest=False, status='pending',
                    requestedAt=(NOW - timedelta(hours=2)).isoformat())

    def test_AK01_production_reader_cannot_certify_unsigned_with_unreadable_request_owner(self):
        source = clean_source({'U1': raw_invite(hours=13)})
        application_client = SimpleNamespace(pages=lambda *a, **kw: [self.unreadable()])
        gate, sender = self.production_gate(source, application_client, self.contract_for())
        result = self.reminder(gate, self.contract_for())
        self.assertEqual(sender.delivered, [],
                         f'Unreadable request owner became proof of no requests: {result.outcome}: {result.reasons}')

    def test_AK01_draft_flow_cannot_withdraw_with_unreadable_request_owner(self):
        contract = self.contract_for()
        source = clean_source({'U1': raw_invite(hours=40)})
        contracts = SimpleNamespace(pages=lambda *a, **kw: [dict(contract)],
                                    request=lambda *a, **kw: {'data': dict(contract)})
        gate, sender = self.configured(source, contract)
        gate.types = {key: replace(t, mode='draft') for key, t in policy.load().items()}
        writes = []
        job = flow.Flow(contracts, source, gate, self.j, lambda chat: ('route1', 'person1'),
                        now=lambda: NOW, write_client=self.writer(writes),
                        read_client=SimpleNamespace(pages=lambda *a, **kw: [self.unreadable()]))
        report = job.run()
        self.assertEqual(sender.delivered, [])
        self.assertEqual(writes, [], f'Unreadable owner became known-empty coverage in all three reads: {report}')


class RecordEntryPoint(EntryPointCase):
    def read_record(self, concurrent=False, resource='chat'):
        clock, writes, reports, consumed = [1000.0], [], [], []
        row = raw_invite(hours=35 + 59 / 60 if concurrent else 10)
        source = clean_source({'U1': row})
        now = lambda: NOW + timedelta(seconds=clock[0] - 1000.0)

        def wait_after_evidence():
            clock[0] += 120.0
            if concurrent:
                reports.extend(self.concurrent_withdrawal(source, 1, now, writes))
            raise KeyboardInterrupt('interrupted waiting for the next page')

        class Chats:
            def pages(inner, path, **kw):
                if path == '/conversations':
                    yield dict(id='chat1', members=[flow.COMPANY, 'U1'],
                               participants=[dict(id='U1', name='Ada Example')])
                    return
                self.assertEqual(path, '/support-channels/chat1/messages')
                yield row
                consumed.append('notice1')
                yield raw_request()
                wait_after_evidence()

        class Contracts:
            def pages(inner, path, **kw):
                self.assertEqual(path, '/contracts')
                if resource == 'contracts':
                    consumed.append('active-C1')
                    yield self.contract_for() | {'status': 'active'}
                    wait_after_evidence()
                else:
                    yield self.contract_for()

        with ExitStack() as stack:
            self.offline_modules(stack, lambda key=None: Chats() if key is None else Contracts())
            stack.enter_context(patch.object(sys, 'argv', ['record.py', 'show', 'U1']))
            stack.enter_context(patch.object(record, 'Journal', return_value=self.j))
            stack.enter_context(patch('time.monotonic', side_effect=lambda: clock[0]))
            with self.assertRaises(KeyboardInterrupt):
                record.main()
        self.assertEqual(consumed, ['notice1' if resource == 'chat' else 'active-C1'])
        self.assertEqual(clock[0], 1120.0)
        return source, writes, reports

    def test_AK02_record_show_consumed_notice_survives_restart_until_later_reminder(self):
        source, _, _ = self.read_record()
        self.later_reminder(source)

    def test_AK02_record_show_consumed_notice_stops_concurrent_withdrawal(self):
        _, writes, reports = self.read_record(concurrent=True)
        self.assertEqual(writes, [], f'record.show consumed signing 120 seconds earlier: {reports}')

    def test_AK02_record_contract_listing_keeps_active_evidence_before_next_page(self):
        source, _, _ = self.read_record(resource='contracts')
        self.later_reminder(source)


class SeedEntryPoint(EntryPointCase):
    def test_AK02_seed_contract_listing_keeps_active_evidence_before_next_page(self):
        clock, consumed = [1000.0], []
        source = clean_source({'U1': raw_invite()})

        class Contracts:
            def pages(inner, path, **kw):
                self.assertEqual(path, '/contracts')
                consumed.append('active-C1')
                yield self.contract_for() | {'status': 'active'}
                clock[0] += 120.0
                raise KeyboardInterrupt('interrupted waiting for the next contract page')

        with ExitStack() as stack:
            self.offline_modules(stack, lambda key=None: Contracts())
            stack.enter_context(patch('gate.journal.Journal', return_value=self.j))
            stack.enter_context(patch('time.monotonic', side_effect=lambda: clock[0]))
            with self.assertRaises(KeyboardInterrupt):
                runpy.run_module('seed_journal', run_name='__main__')
        self.assertEqual(consumed, ['active-C1'])
        self.assertEqual(clock[0], 1120.0)
        self.later_reminder(source)
