"""Offline required-behavior regressions. No production edits or network.
Run: python3 -m unittest discover -s out/tests -t .
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from gate import checks
from gate.tests.review3.support import Case, NOW, grant
from gate.tests.review35 import test_round35 as fixtures


class Review42(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw

    def writer(self):
        self.writes = []
        self.job.write_client = SimpleNamespace(
            request=lambda *a, **kw: self.writes.append((a, kw)) or
            dict(id='C1', contractorId='U1', status='rejected'))

    def test_BD01_first_read_deleted_question_cannot_authorize_draft_only_withdrawal(self):
        self.setup_flow()
        self.g.types = {k: replace(t, mode='draft') for k, t in self.g.types.items()}
        self.rows[0]['createdAt'] = (self.clock - timedelta(hours=40)).isoformat()
        self.rows.append(dict(id='question', createdAt=(self.clock - timedelta(hours=30)).isoformat(),
                              senderUserId='U1', content='What should I film for the first video?', isDeleted=True))
        self.writer()
        report = self.job.run()
        self.assertEqual(self.j.flags('sideshift:U1', 'answered'), set())
        self.assertEqual(self.writes, [], f'A deletion flag alone settled a readable question: {report}')

    def test_BD01_first_read_deleted_file_still_needs_review_before_reminder(self):
        self.setup_flow()
        self.rows.append(dict(id='draft', createdAt=(self.clock - timedelta(hours=4)).isoformat(),
                              senderUserId='U1', content='My draft', isDeleted=True,
                              attachments=[{'id': 'never-reviewed-file'}]))
        report = self.job.run()
        self.assertEqual(self.j.flags('sideshift:U1', 'attachment-reviewed'), set())
        self.assertEqual(self.sender.delivered, [], f'A readable file never reviewed permits a reminder: {report}')

    def test_BD02_reply_cannot_use_review_that_missed_newly_remembered_question(self):
        self.setup_flow()
        shown = []
        def review(conv, *args):
            shown.append(conv)
            # Another read-only process observes a message while this review is
            # running. Use a second real reader/journal connection, as record.py
            # would. It need not own the gate's sending reservation to observe.
            self.observe_then_remove_question()
            return 'SEND', 'The supplied conversation has no open questions.', []
        self.g.reviewer = review
        with patch('time.time', side_effect=lambda: self.clock.timestamp()), \
                patch('time.monotonic', side_effect=lambda: (self.clock - NOW).total_seconds()):
            result = self.g.run(self.action(message_type='at-capacity', fields={'First': 'Ada'},
                                           contract=dict(self.current)))
        self.assertEqual(len(shown), 1)
        self.assertFalse(any(m.id == 'new-question' for m in shown[0].messages))
        final = checks.with_history(self.source.read('chat1'), self.j.events('sideshift:U1'))
        self.assertTrue(any(m.id == 'new-question' for m in checks.unanswered(final)))
        self.assertEqual(self.sender.delivered, [],
                         f'Reply was never reviewed against the question now in its evidence: {result}')

    def observe_then_remove_question(self):
        from gate.journal import Journal
        from gate.live import SideShiftLive
        other = Journal(self.root / 'gate.db')
        try:
            self.rows.append(dict(id='new-question', createdAt=self.clock.isoformat(),
                                  senderUserId='U1', content='Can you confirm the payment amount before I continue?'))
            source = SideShiftLive(self.source.client, self.job.live.company_id, on_notice=other.remember_notice)
            source.read('chat1', ['U1'])
            self.rows.pop()
            # Every subsequent remote read is stable, well outside the 10s
            # allowance. The permanent journal still contains the question.
            self.clock += timedelta(minutes=2)
        finally:
            other.conn.close()

    def test_BD02_premium_cannot_be_granted_under_review_missing_known_question(self):
        self.setup_flow()
        self.current['status'] = 'active'
        email = 'ada@example.com'
        self.rows.append(dict(id='email', createdAt=(self.clock - timedelta(hours=1)).isoformat(),
                              senderUserId='U1', content=email))
        commands = []
        active = [False]
        def runner(argv, **kwargs):
            commands.append(argv)
            if argv[1] == 'grant':
                active[0] = True
                word = 'GRANTED'
            else:
                word = 'ACTIVE' if active[0] else 'NONE'
            return SimpleNamespace(returncode=0, stdout=f'{word}: {email}', stderr='')
        self.g.granter = lambda a: grant.grant(self.j, a.creator_key, email, 'offline review', runner)
        def review(conv, *args):
            self.assertFalse(any(m.id == 'new-question' for m in conv.messages))
            self.observe_then_remove_question()
            return 'SEND', 'The supplied conversation only requests Premium.', []
        self.g.reviewer = review
        with patch('time.time', side_effect=lambda: self.clock.timestamp()), \
                patch('time.monotonic', side_effect=lambda: (self.clock - NOW).total_seconds()):
            result = self.g.run(self.action(message_type='app-access', fields={'email': email},
                                           contract=dict(self.current)))
        self.assertEqual([cmd for cmd in commands if cmd[1] == 'grant'], [],
                         f'Newly known payment question never reached review before grant: {result}; {commands}')
