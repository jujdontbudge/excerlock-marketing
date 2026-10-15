"""Offline required-behavior regressions for round 44; production code unchanged.
Run: python3 -m unittest discover -s out/tests -t .
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks
from gate.tests.review3.support import Case, grant, propose
from gate.tests.review35 import test_round35 as fixtures


class Review44(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def bad_media_question(self, draft=False):
        self.setup_flow()
        if draft:
            self.g.types = {key: replace(t, mode='draft') for key, t in self.g.types.items()}
            self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        # Identity, timestamp and the entire question are independently readable.
        # Only the unrelated media count has the wrong type. The actual reader
        # consumes this row before holding, as with the existing AS01 notice case.
        self.rows.append(dict(id='payment-question',
                              createdAt=(self.clock - timedelta(hours=30)).isoformat(),
                              senderUserId='U1', content='What is the payment for my first video?',
                              attachmentCount='1'))
        writes = []
        self.job.write_client = SimpleNamespace(
            request=lambda *a, **kw: writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))
        first = self.job.run()
        self.assertEqual(self.sender.delivered, [], first)
        self.assertEqual(writes, [], first)
        self.assertTrue(any('attachmentCount' in line for line in first), first)
        self.assertFalse(self.j.flags('sideshift:U1', 'answered'))
        # The problematic row disappears upstream. The next scheduled run has
        # fully readable, stable responses, fifteen minutes outside the window.
        self.rows.pop()
        self.clock += timedelta(minutes=15)
        return writes

    def test_BF01_readable_question_with_bad_media_survives_failed_read_before_reminder(self):
        self.bad_media_question()
        reviewed = []
        def reviewer(conv, *args):
            reviewed.append([m.text for m in conv.messages])
            return 'SEND', 'No open question appears in the supplied chat.', []
        self.g.reviewer = reviewer
        later = self.job.run()
        self.assertEqual(self.sender.delivered, [],
                         f'Consumed payment question was lost before the next reminder: {later}; '
                         f'reviewed={reviewed}')

    def test_BF01_readable_question_with_bad_media_survives_all_draft_withdrawal(self):
        writes = self.bad_media_question(draft=True)
        later = self.job.run()
        self.assertEqual(writes, [],
                         f'All-draft Flow withdrew after forgetting the consumed question: {later}')

    def unicode_mailbox(self, option=None, direct=False):
        self.setup_flow()
        self.current['status'] = 'active'
        actual, requested = '\N{KELVIN SIGN}ada@example.com', 'kada@example.com'
        self.assertNotEqual(actual, requested)
        self.assertFalse(actual.isascii())
        # The supported email syntax is ASCII. Lowercasing must not turn an
        # unsupported local part into provenance for a different ASCII account.
        self.rows.append(dict(id='email', createdAt=(self.clock - timedelta(hours=1)).isoformat(),
                              senderUserId='U1', content=actual))
        if option:
            allowed = {'contract-reminder-1', 'contract-reminder-2', 'warmup-guide', 'ask-app-email'} if option == 'c' else set()
            self.g.types = {key: t if key in allowed else replace(t, mode='draft')
                            for key, t in self.g.types.items()}
        commands, active = [], [False]
        def runner(argv, **kw):
            commands.append(argv)
            if argv[1] == 'grant':
                active[0] = True
                word = 'GRANTED'
            else:
                word = 'ACTIVE' if active[0] else 'NONE'
            return SimpleNamespace(returncode=0, stdout=f'{word}: {requested}', stderr='')
        self.g.granter = lambda a: grant.grant(self.j, a.creator_key, a.fields['email'], 'offline review', runner)
        if direct:
            result = self.g.run(self.action(message_type='app-access', fields={'email': requested},
                                           contract=dict(self.current)))
        else:
            detail = dict(id='route1', channel='sideshift', external_id='sideshift:chat1',
                          participants=[dict(value_normalized='U1', person_id='person1',
                                             profile={'display_name': 'Ada Example'})],
                          messages=[dict(id='cached-email', direction='in', text=actual)])
            result = propose.handle(
                dict(id='in1', external_id='sideshift:email', channel='sideshift',
                     conversation_id='route1', text=actual),
                dict(action='template', message_type='app-access', fields={'email': requested}),
                SimpleNamespace(call=lambda *a, **kw: detail), self.g.types,
                [dict(self.current)], self.j, self.g, False)
        self.assertEqual([cmd for cmd in commands if cmd[1] == 'grant'], [],
                         f'Unsupported live mailbox {actual!r} authorized {requested!r}: {result}; {commands}')
        self.assertEqual(self.sender.delivered, [], result)

    def test_BF02_proposer_and_gate_cannot_fold_unicode_into_ascii_mailbox(self):
        self.unicode_mailbox()

    def test_BF02_live_gate_provenance_cannot_fold_unicode_into_ascii_mailbox(self):
        self.unicode_mailbox(direct=True)

    def test_option_b_drafts_contain_BF02(self):
        self.unicode_mailbox(option='b')

    def test_option_c_premium_drafts_contain_BF02(self):
        self.unicode_mailbox(option='c')
