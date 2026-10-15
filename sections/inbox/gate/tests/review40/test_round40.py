"""Offline required-behavior regressions; no production changes or network.
Run: python3 -m unittest discover -s out/tests -t .
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.tests.review3.support import Case, grant, propose
from gate.tests.review35 import test_round35 as fixtures


class EvidenceBoundaries(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def add_file(self, hours=4):
        self.rows.append(dict(id='draft', createdAt=(self.clock - timedelta(hours=hours)).isoformat(),
                              senderUserId='U1', content='My draft', attachments=[{'id': 'unreviewed-file'}]))
        return next(m for m in self.source.read('chat1').messages if m.id == 'draft')

    def writer(self):
        writes = []
        self.job.write_client = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                               dict(id='C1', contractorId='U1', status='rejected'))
        return writes

    def test_BB01_sender_change_cannot_erase_observed_inbound_file_before_reminder(self):
        self.setup_flow()
        original = self.add_file()
        first = self.job.run()
        self.assertEqual(self.sender.delivered, [], first)
        self.assertTrue(any('attachment' in line for line in first), first)
        self.assertNotIn(checks.mark(original), self.j.flags('sideshift:U1', 'attachment-reviewed'))
        # The native row retains its id, words, deletion state and file id;
        # the service changes its sender attribution to the company.
        self.rows[-1]['senderUserId'] = self.job.live.company_id
        self.clock += timedelta(minutes=15)
        second = self.job.run()
        self.assertEqual(self.sender.delivered, [],
                         f'Previously observed inbound file lost its review veto: {second}')

    def test_BB01_sender_change_cannot_erase_observed_file_before_draft_only_withdrawal(self):
        self.setup_flow()
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        original = self.add_file(hours=30)
        self.j.event('sideshift:U1', 'answered', checks.mark(original), {'by': 'captain'})
        writes = self.writer()
        first = self.job.run()
        self.assertEqual(writes, [], first)
        self.assertTrue(any('attachment' in line for line in first), first)
        self.rows[-1]['senderUserId'] = self.job.live.company_id
        self.clock += timedelta(minutes=15)
        second = self.job.run()
        self.assertEqual(writes, [], f'Unreviewed inbound file forgotten and all-draft Flow rejected invite: {second}')

    def test_BB01_retimestamp_cannot_erase_observed_recent_activity_before_withdrawal(self):
        self.setup_flow()
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        self.rows.append(dict(id='trying', createdAt=(self.clock - timedelta(hours=1)).isoformat(),
                              senderUserId='U1', content='I am still trying to create the accounts.'))
        original = self.source.read('chat1').messages[-1]
        # Settle the words only. The separate 24h activity veto still applies.
        self.j.event('sideshift:U1', 'answered', checks.mark(original), {'by': 'captain'})
        writes = self.writer()
        first = self.job.run()
        self.assertEqual(writes, [], first)
        self.assertTrue(any('last 24 hours' in line for line in first), first)
        self.rows[-1]['createdAt'] = (self.clock - timedelta(hours=30)).isoformat()
        self.clock += timedelta(minutes=15)
        second = self.job.run()
        self.assertEqual(writes, [], f'Retimestamping erased an observed 75-minute-old message: {second}')

    def test_BB02_embedded_apostrophe_cannot_authorize_suffix_account_grant(self):
        self.setup_flow()
        self.current['status'] = 'active'
        requested, actual = 'ada@example.com', "o'ada@example.com"
        # An apostrophe inside a mailbox is not an opening quote around the
        # requested address. Contacts has the stale shorter address.
        self.rows.append(dict(id='email', createdAt=(self.clock - timedelta(hours=1)).isoformat(),
                              senderUserId='U1', content=actual))
        commands, entitlement = [], ['NONE']
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
                         f'Live mailbox {actual!r} authorized suffix {requested}: {outcome}; {commands}')

    def test_BB03_tombstone_cannot_settle_an_unanswered_question_before_draft_only_withdrawal(self):
        self.setup_flow()
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        self.rows.append(dict(id='question', createdAt=(self.clock - timedelta(hours=30)).isoformat(),
                              senderUserId='U1', content='What should I film for the first video?'))
        original = self.source.read('chat1').messages[-1]
        writes = self.writer()
        first = self.job.run()
        self.assertEqual(writes, [], first)
        self.assertTrue(any('waiting for an answer' in line for line in first), first)
        self.assertNotIn(checks.mark(original), self.j.flags('sideshift:U1', 'answered'))
        # BA01 now keeps the old revision separately, but with_history marks
        # a text-only predecessor as deleted, which unanswered ignores.
        self.rows[-1]['isDeleted'] = True
        self.clock += timedelta(minutes=15)
        second = self.job.run()
        self.assertEqual(writes, [], f'A deletion flag settled a question nobody answered: {second}')
