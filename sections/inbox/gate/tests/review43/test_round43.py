"""Required-behavior counterexamples, real gate/reader/grant/CLI; no network.
Run: python3 -m unittest discover -s out/tests -t .
"""
from dataclasses import replace
from datetime import timedelta
from email.headerregistry import Address
from types import SimpleNamespace

from gate import checks
from gate.live import revision_key
from gate.tests.review3.support import Case, grant, propose
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review39 import test_round39 as record_fixtures


class Review43(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw
    run_record = record_fixtures.RevisionBoundaries.run_record

    def check_prefix_mailbox(self, actual, option=None):
        self.setup_flow()
        self.current['status'] = 'active'
        self.assertEqual(Address(addr_spec=actual).addr_spec, actual)
        if option:
            allowed = {'contract-reminder-1', 'contract-reminder-2', 'warmup-guide', 'ask-app-email'} if option == 'c' else set()
            self.g.types = {key: t if key in allowed else replace(t, mode='draft')
                            for key, t in self.g.types.items()}
        requested = 'ada@example.com'
        # The complete live mailbox differs from the proposed suffix. Even an
        # unsupported mailbox must hold, rather than authorize another account.
        self.rows.append(dict(id='email', createdAt=(self.clock - timedelta(hours=1)).isoformat(),
                              senderUserId='U1', content=actual))
        commands = []
        active = [False]
        def runner(argv, **kw):
            commands.append(argv)
            if argv[1] == 'grant':
                active[0] = True
                word = 'GRANTED'
            else:
                word = 'ACTIVE' if active[0] else 'NONE'
            return SimpleNamespace(returncode=0, stdout=f'{word}: {requested}', stderr='')
        self.g.granter = lambda a: grant.grant(self.j, a.creator_key, a.fields['email'], 'offline review', runner)
        # Use the real proposal builder too: contacts has exactly her live text,
        # not an invented or shorter cached mailbox.
        detail = dict(id='route1', channel='sideshift', external_id='sideshift:chat1',
                      participants=[dict(value_normalized='U1', person_id='person1',
                                         profile={'display_name': 'Ada Example'})],
                      messages=[dict(id='cached-email', direction='in', text=actual)])
        contacts = SimpleNamespace(call=lambda *a, **kw: detail)
        result = propose.handle(
            dict(id='in1', external_id='sideshift:email', channel='sideshift',
                 conversation_id='route1', text=actual),
            dict(action='template', message_type='app-access', fields={'email': requested}),
            contacts, self.g.types, [dict(self.current)], self.j, self.g, False)
        self.assertEqual([cmd for cmd in commands if cmd[1] == 'grant'], [],
                         f'Live mailbox {actual!r} authorized a different account: {result}; {commands}; '
                         f'deliveries={self.sender.delivered}')
        self.assertEqual(self.sender.delivered, [], result)

    def test_BE01_leading_apostrophe_is_not_proof_of_suffix_mailbox(self):
        self.check_prefix_mailbox("'ada@example.com")

    def test_BE01_leading_bang_is_not_proof_of_suffix_mailbox(self):
        self.check_prefix_mailbox('!ada@example.com')

    def test_option_b_drafts_contain_BE01(self):
        self.check_prefix_mailbox("'ada@example.com", option='b')

    def test_option_c_premium_drafts_contain_BE01(self):
        self.check_prefix_mailbox("'ada@example.com", option='c')

    def deleted_inbound(self, text, **kw):
        self.setup_flow()
        self.rows.append(dict(id='deleted', createdAt=(self.clock - timedelta(hours=4)).isoformat(),
                              senderUserId='U1', content=text, isDeleted=True, **kw))
        return next(m for m in self.source.read('chat1').messages if m.id == 'deleted')

    def test_BE02_captain_can_mark_exact_deleted_question_answered(self):
        m = self.deleted_inbound('What should I film?')
        self.assertTrue(checks.unanswered(self.source.read('chat1')))
        output = self.run_record('answered', revision_key(m))
        self.assertIn(checks.mark(m), self.j.flags('sideshift:U1', 'answered'),
                      f'Exact unresolved deleted revision cannot be settled: {output}')

    def test_BE02_captain_can_mark_exact_deleted_file_looked_at(self):
        m = self.deleted_inbound('My draft', attachments=[{'id': 'reviewed-by-captain'}])
        self.assertTrue(checks.completeness(self.source.read('chat1')))
        output = self.run_record('looked-at', revision_key(m))
        self.assertIn(checks.mark(m), self.j.flags('sideshift:U1', 'attachment-reviewed'),
                      f'Exact unresolved deleted file cannot be settled: {output}')
