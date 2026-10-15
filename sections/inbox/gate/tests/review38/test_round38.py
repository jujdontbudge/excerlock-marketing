"""Required-behavior regressions for round 38; fakes only, no network.
Run: python3 -m unittest discover -s out/tests -t .
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace

from gate import checks, policy
from gate.tests.review3.support import Case, grant
from gate.tests.review35 import test_round35 as fixtures


class HistoryBoundaries(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def test_AZ01_observed_attachment_revision_survives_row_loss_before_withdrawal(self):
        self.setup_flow()
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        self.rows.append(dict(id='draft', createdAt=(self.clock - timedelta(hours=30)).isoformat(),
                              senderUserId='U1', content='My draft'))
        original = self.source.read('chat1').messages[-1]
        self.j.event('sideshift:U1', 'answered', checks.mark(original), {'by': 'captain'})
        # Same message text, but she adds a file; the old mark cannot cover it.
        self.rows[-1]['attachments'] = [{'id': 'unreviewed-draft'}]
        writes = []
        self.job.write_client = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                               dict(id='C1', contractorId='U1', status='rejected'))
        held = self.job.run()
        self.assertEqual(writes, [], held)
        self.assertTrue(any('attachment' in line for line in held), held)
        # Fifteen minutes later the complete upstream chat omits this row.
        self.rows.pop()
        self.clock += timedelta(minutes=15)
        report = self.job.run()
        self.assertEqual(writes, [], f'An observed unreviewed attachment was forgotten: {report}')

    def test_AZ01_observed_attachment_revision_survives_row_loss_before_reminder(self):
        self.setup_flow()
        self.rows.append(dict(id='draft', createdAt=(self.clock - timedelta(hours=4)).isoformat(),
                              senderUserId='U1', content='My draft'))
        original = self.source.read('chat1').messages[-1]
        self.j.event('sideshift:U1', 'answered', checks.mark(original), {'by': 'captain'})
        self.rows[-1]['attachments'] = [{'id': 'unreviewed-draft'}]
        held = self.job.run()
        self.assertEqual(self.sender.delivered, [], held)
        self.assertTrue(any('attachment' in line for line in held), held)
        self.rows.pop()
        self.clock += timedelta(minutes=15)
        report = self.job.run()
        self.assertEqual(self.sender.delivered, [],
                         f'An automatic reminder follows an observed unreviewed file: {report}')

    def test_AZ02_missing_email_is_veto_history_not_live_grant_authority(self):
        self.setup_flow()
        self.current['status'] = 'active'
        email = 'ada@example.com'
        self.rows.append(dict(id='email', createdAt=(self.clock - timedelta(hours=1)).isoformat(),
                              senderUserId='U1', content=email))
        self.source.read('chat1')  # real reader hook persists her email
        self.rows.pop()
        self.clock += timedelta(minutes=15)
        # Proposal may originate in the stale contacts inbox; all gate reads now
        # agree the email is absent. There is no within-window race.
        commands = []
        def runner(args, **kw):
            commands.append(args)
            word = 'NONE' if args[1] == 'check' else 'GRANTED'
            return SimpleNamespace(returncode=0, stdout=f'{word}: {email}', stderr='')
        self.g.granter = lambda a: grant.grant(self.j, a.creator_key, email, 'offline review', runner)
        result = self.g.run(self.action(message_type='app-access', fields={'email': email},
                                       contract=dict(self.current)))
        self.assertEqual([args for args in commands if args[1] == 'grant'], [],
                         f'Vanished historical email authorizes a new grant: {result.outcome}; {commands}')

    def test_AZ03_successful_reply_marks_the_vanished_question_the_reviewer_saw(self):
        self.setup_flow()
        self.current['status'] = 'active'
        self.rows.append(dict(id='question', createdAt=(self.clock - timedelta(hours=1)).isoformat(),
                              senderUserId='U1', content='How do I sign in?'))
        question = self.source.read('chat1').messages[-1]
        self.rows.pop()
        self.clock += timedelta(minutes=15)
        # Approved one-use captain-text takes the real reply path without a
        # Premium grant, and marks every question its full-chat review settles.
        text = 'Tap Already have an account, then Continue with email.'
        a = self.action(message_type='captain-text', fields={'text': text},
                        contract=dict(self.current), captain_order='Send these exact words')
        from gate.dispatch import text_hash
        a.approval_id = self.j.approve(a.creator_key, a.message_type, a.occurrence,
                                      text_hash(text), a.captain_order)
        shown = []
        def reviewer(conv, *args):
            shown.extend(conv.messages)
            return 'SEND', 'This answers the sign-in question fully.', []
        self.g.reviewer = reviewer
        result = self.g.run(a)
        self.assertEqual(result.outcome, 'sent', result.reasons)
        self.assertTrue(any(m.id == 'question' and m.vanished for m in shown))
        self.assertEqual(len(self.sender.delivered), 1)
        self.assertIn(checks.mark(question), self.j.flags(a.creator_key, 'answered'),
                      'Reply was delivered, but only raw live messages are marked answered')
