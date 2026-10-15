"""Offline required-behavior regressions; fail against the reviewed snapshot.

Run: python3 -m unittest discover -s out/tests -t .
Real reader, gate, journal, flow, grant, record CLI and ContactsMCP boundary.
Only service responses, model verdict, clock and access commands are faked.
"""
import sys
from contextlib import ExitStack, redirect_stdout
from dataclasses import replace
from datetime import timedelta
from io import StringIO
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from gate import checks, policy
from gate.tests.review3.support import Case, grant, propose
from gate.tests.review35 import test_round35 as fixtures
import record


class RevisionBoundaries(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def add_file(self, hours=4, file_id='unreviewed-file'):
        self.rows.append(dict(id='draft', createdAt=(self.clock - timedelta(hours=hours)).isoformat(),
                              senderUserId='U1', content='My draft', attachments=[{'id': file_id}]))
        return next(m for m in self.source.read('chat1').messages if m.id == 'draft')

    def test_BA01_deleted_flag_cannot_erase_observed_file_before_reminder(self):
        self.setup_flow()
        original = self.add_file()
        first = self.job.run()
        self.assertEqual(self.sender.delivered, [], first)
        self.assertTrue(any('attachment' in line for line in first), first)
        self.assertNotIn(checks.mark(original), self.j.flags('sideshift:U1', 'attachment-reviewed'))
        # Same id, text and attachment; only the native deletion flag changes.
        # All later reads agree. Fifteen minutes exceeds the accepted 10s gap.
        self.rows[-1]['isDeleted'] = True
        self.clock += timedelta(minutes=15)
        second = self.job.run()
        self.assertEqual(self.sender.delivered, [],
                         f'Deletion flag erased an observed unreviewed file: {second}')

    def test_BA01_deleted_flag_cannot_erase_observed_file_before_draft_only_withdrawal(self):
        self.setup_flow()
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        original = self.add_file(hours=30)
        # Answering its words is separate from reviewing its file.
        self.j.event('sideshift:U1', 'answered', checks.mark(original), {'by': 'captain'})
        writes = []
        self.job.write_client = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                               dict(id='C1', contractorId='U1', status='rejected'))
        first = self.job.run()
        self.assertEqual(writes, [], first)
        self.assertTrue(any('attachment' in line for line in first), first)
        self.rows[-1]['isDeleted'] = True
        self.clock += timedelta(minutes=15)
        second = self.job.run()
        self.assertEqual(writes, [],
                         f'All message types are draft, but deleting the unreviewed file permits rejection: {second}')

    def test_BA02_live_different_mailbox_cannot_authorize_suffix_account_grant(self):
        self.setup_flow()
        self.current['status'] = 'active'
        requested, actual = 'ada@example.com', 'alias%ada@example.com'
        self.assertTrue(policy.valid('email', actual))
        # Cached contacts saw the old mailbox. Her live edited row now says a
        # different valid mailbox; the gate must validate the complete token.
        self.rows.append(dict(id='email', createdAt=(self.clock - timedelta(hours=1)).isoformat(),
                              senderUserId='U1', content=actual))
        commands = []
        entitlement = ['NONE']

        def runner(argv, **kw):
            commands.append(argv)
            if argv[1] == 'grant':
                entitlement[0] = 'ACTIVE'
                word = 'GRANTED'
            else:
                word = entitlement[0]
            return SimpleNamespace(returncode=0, stdout=f'{word}: {requested}', stderr='')

        self.g.granter = lambda a: grant.grant(self.j, a.creator_key, a.fields['email'], 'offline review', runner)
        detail = dict(id='route1', channel='sideshift', external_id='sideshift:chat1',
                      participants=[dict(value_normalized='U1', person_id='person1',
                                         profile={'display_name': 'Ada Example'})],
                      messages=[dict(id='cached-email', direction='in', text=requested)])
        contacts = SimpleNamespace(call=lambda *a, **kw: detail)
        outcome = propose.handle(
            dict(id='in1', external_id='sideshift:email', channel='sideshift',
                 conversation_id='route1', text=requested),
            dict(action='template', message_type='app-access', fields={'email': requested}),
            contacts, self.g.types, [dict(self.current)], self.j, self.g, False)
        self.assertEqual([cmd for cmd in commands if cmd[1] == 'grant'], [],
                         f'Current live mailbox is {actual}, but {requested} was granted: {outcome}; {commands}')

    def run_record(self, command, mid):
        client_module = ModuleType('client')
        client_module.Client = lambda *a: (SimpleNamespace(pages=lambda *a, **kw: [])
                                           if a else self.source.client)
        dotenv = ModuleType('dotenv')
        dotenv.load_dotenv = lambda *a: None
        with ExitStack() as stack:
            stack.enter_context(patch.dict(sys.modules, {'client': client_module, 'dotenv': dotenv}))
            stack.enter_context(patch.dict('os.environ', {'SIDESHIFT_CONTRACTS_KEY': 'offline'}))
            stack.enter_context(patch.object(record, 'find_creator', return_value=('U1', 'Ada', 'chat1')))
            stack.enter_context(patch.object(record, 'Journal', return_value=self.j))
            # Preserve the real SideShiftLive implementation and journal hook;
            # use only the fake HTTP client's pages from setup_flow.
            stack.enter_context(patch.object(sys, 'argv', ['record.py', command, 'Ada', mid]))
            output = stack.enter_context(redirect_stdout(StringIO()))
            record.main()
        return output.getvalue()

    def test_BA03_looked_at_id_cannot_silently_review_a_different_historical_file(self):
        self.setup_flow()
        old = self.add_file(file_id='old-unseen-file')
        self.rows[-1]['attachments'] = [{'id': 'current-file'}]
        current = next(m for m in self.source.read('chat1').messages if m.id == 'draft')
        output = self.run_record('looked-at', 'draft')
        # Both share one native id. The CLI must either mark the current file
        # or ask for an exact revision, never silently mark the unseen old file.
        reviewed = self.j.flags('sideshift:U1', 'attachment-reviewed')
        self.assertNotIn(checks.mark(old), reviewed,
                         f'Looking at the current file marked its unseen predecessor: {output}; {reviewed}')
        if reviewed:
            self.assertIn(checks.mark(current), reviewed)

