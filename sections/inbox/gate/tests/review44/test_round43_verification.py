"""Additional checks of round-43 repairs, using direct gate and real record CLI."""
from datetime import timedelta

from gate import checks
from gate.live import revision_key
from gate.tests.review3.support import Case
from gate.tests.review35 import test_round35 as fixtures
from gate.tests.review39 import test_round39 as record_fixtures


class Round43Verification(Case):
    setup_flow = fixtures.RetainedDelivery.setup_flow
    raw = fixtures.RetainedDelivery.raw
    run_record = record_fixtures.RevisionBoundaries.run_record

    def test_BE01_direct_live_gate_rejects_leading_mailbox_characters(self):
        self.setup_flow()
        self.current['status'] = 'active'
        called = []
        self.g.granter = lambda action: (called.append(action) or True, 'must not run')
        for i, text in enumerate(("'ada@example.com", '!ada@example.com',
                                  "o'ada@example.com", 'alias%ada@example.com')):
            with self.subTest(text=text):
                self.rows = self.rows[:1] + [dict(id=f'email-{i}', senderUserId='U1', content=text,
                                                 createdAt=(self.clock - timedelta(hours=1)).isoformat())]
                result = self.g.run(self.action(message_type='app-access', fields={'email': 'ada@example.com'},
                                               contract=dict(self.current)))
                self.assertEqual(called, [], result)
                self.assertEqual(self.sender.delivered, [], result)
                self.assertIn('the email is not in her own live messages', result.reasons)

    def test_BE01_only_matched_whole_wrappers_authorize_supported_email(self):
        for text in ('<ada@example.com>.', '(ada@example.com)', '[ada@example.com]',
                     '"ada@example.com"', "'ada@example.com'"):
            with self.subTest(text=text):
                self.assertEqual(checks.email_tokens(text), {'ada@example.com'})
        self.assertEqual(checks.email_tokens("'ada@example.com and !ada@example.com"), set())

    def add_deleted_question(self):
        self.rows.append(dict(id='deleted-question', senderUserId='U1', content='What should I film?',
                              createdAt=(self.clock - timedelta(hours=30)).isoformat(), isDeleted=True))
        return next(m for m in self.source.read('chat1').messages if m.id == 'deleted-question')

    def test_BE02_unambiguous_native_id_can_settle_deleted_revision(self):
        self.setup_flow()
        m = self.add_deleted_question()
        result = self.run_record('answered', m.id)
        self.assertIn(checks.mark(m), self.j.flags('sideshift:U1', 'answered'), result)

    def test_BE02_deleted_revision_ambiguity_lists_both_and_marks_neither(self):
        self.setup_flow()
        old = self.add_deleted_question()
        self.rows[-1]['content'] = 'When is payment?'
        new = next(m for m in self.source.read('chat1').messages if m.id == old.id)
        result = self.run_record('answered', old.id)
        # adapted 2026-10-15 (review CH01): the words changed without an edit clock, so both versions are listed with
        # their timing marked unknown (different keys than the raw read); still both listed, neither marked
        self.assertIn(repr(old.text), result)
        self.assertIn(repr(new.text), result)
        self.assertEqual(self.j.flags('sideshift:U1', 'answered'), set(), result)
