import json
import os
import sqlite3
from dataclasses import replace
from datetime import timedelta
from unittest.mock import patch

from gate import checks
from gate.journal import Journal, SCHEMA, snapshot
from gate.live import SideShiftLive
from gate.model import Decision, IN
from .support import Case, NOW, Live, Sender, conv, flow, handles, invite, msg, seed_journal, withdraw


class StateAndJournal(Case):
    def test_N27_tied_timestamps_do_not_invent_captain_answer_coverage(self):
        class Client:
            def pages(inner, path):
                if path == '/conversations':
                    return [{'id': 'chat1', 'members': ['COMPANY', 'U1']}]
                return [dict(id='z-captain', createdAt=NOW.isoformat(), senderUserId='COMPANY', content='Hello'),
                        dict(id='a-question', createdAt=NOW.isoformat(), senderUserId='U1', content='What is my rate?')]
        c = SideShiftLive(Client(), 'COMPANY').read('chat1')
        self.assertEqual([m.id for m in checks.unanswered(c)], ['a-question'], 'Lexical IDs invent a later answer at the same source timestamp')

    def test_N28_impossible_approval_date_cannot_enable_automatic_sends(self):
        from gate import policy
        p = self.root / 'example.md'
        p.write_text('---\nid: example\nmode: auto\nchannel: sideshift\napproved: 2026-99-99\nfields: []\nonce: per_creator\n---\nApproved text.')
        try:
            t = policy.parse(p)
        except policy.PolicyError:
            return
        self.assertNotEqual(t.effective_mode, 'auto')

    def test_N16_interleaved_approval_repost_is_not_a_new_invitation(self):
        original = invite(at=NOW - timedelta(hours=12))
        request = msg('h', '📨 Requested 2 handles: @new (tiktok), @new (instagram) for this contract.',
                      direction=IN, at=NOW - timedelta(hours=11))
        approved = msg('a', '✅ Your handle @new (tiktok) was approved for this contract.', at=NOW - timedelta(hours=10))
        interleaved = msg('text', 'Thanks for linking!', at=NOW - timedelta(hours=10) + timedelta(minutes=1))
        repost = invite('repost', at=NOW - timedelta(hours=10) + timedelta(minutes=2))
        c = conv(original, request, approved, interleaved, repost)
        self.assertTrue(checks.maybe_accepted(c, self.contract()), 'Repost resets invite time past the genuine request')

    def test_N16_repost_after_five_minutes_does_not_erase_signing_evidence(self):
        c = conv(invite(at=NOW - timedelta(hours=12)),
                 msg('h', '📨 Requested handle @new (tiktok) for this contract.', direction=IN, at=NOW - timedelta(hours=11)),
                 msg('a', '✅ Your handle @new (tiktok) was approved for this contract.', at=NOW - timedelta(hours=10)),
                 invite('repost', at=NOW - timedelta(hours=10) + timedelta(minutes=6)))
        self.assertTrue(checks.maybe_accepted(c, self.contract()))

    def test_N16_inbound_approval_text_cannot_hide_a_real_invite(self):
        old = invite('old', at=NOW - timedelta(hours=40))
        typed = msg('fake', '✅ Your handle @new (tiktok) was approved for this contract.', direction=IN,
                    at=NOW - timedelta(hours=1, minutes=1))
        new = invite('new', at=NOW - timedelta(hours=1))
        self.assertEqual(checks.invite_generation(conv(old, typed, new), self.contract()), 'new')

    def test_N17_transient_profile_error_is_retried(self):
        attempts = []
        def fetch(h):
            attempts.append(h)
            return handles.Profile('tiktok', h, False, error='Timeout') if len(attempts) == 1 else handles.Profile('tiktok', h, True, NOW, 0, 0)
        source = conv(invite(), msg('h', '📨 Requested 2 handles: @new (tiktok), @new (instagram) for this contract.', direction=IN))
        f = flow.Flow(None, None, None, self.j, None, now=lambda: NOW,
                      fetchers={'tiktok': fetch, 'instagram': lambda h: handles.Profile('instagram', h, True, None, 0, 0)})
        f.check_handles('sideshift:U1', source, self.contract())
        f.check_handles('sideshift:U1', source, self.contract())
        self.assertEqual(len(attempts), 2, 'A transient ask verdict is stored as finished work forever')

    def test_N17_edited_handle_request_is_checked_again(self):
        fetched = []
        def fetch(h):
            fetched.append(h)
            return handles.Profile('tiktok', h, True, NOW, 0, 0)
        r = msg('h', '📨 Requested handle @old (tiktok) for this contract.', direction=IN)
        f = flow.Flow(None, None, None, self.j, None, now=lambda: NOW, fetchers={'tiktok': fetch})
        f.check_handles('sideshift:U1', conv(invite(), r), self.contract())
        f.check_handles('sideshift:U1', conv(invite(), replace(r, text=r.text.replace('@old', '@new'))), self.contract())
        self.assertIn('new', fetched)

    def test_N18_snapshot_uses_configured_journal_including_wal(self):
        configured = self.root / 'configured.db'
        j = self.new_journal(configured)
        a = self.action()
        key = self.gate().key(self.type, a)
        j.record(a, key, Decision('sent', ['committed in configured WAL']))
        with patch.dict(os.environ, {'INBOX_GATE_DB': str(configured)}), patch('gate.journal.DEFAULT', self.root / 'unused-default.db'):
            copied = snapshot(self.root / 'copy.db')
        self.addCleanup(copied.conn.close)
        self.assertTrue(copied.spent(key), 'Dry-run copied DEFAULT instead of the journal production opens')

    def test_N19_migration_never_exposes_mutable_decisions(self):
        path = self.root / 'old.db'
        old = sqlite3.connect(path, isolation_level=None)
        old.executescript(SCHEMA.replace("'uncertain','dispatching'", "'uncertain'"))
        old.execute("INSERT INTO decisions (at,creator_key,channel,conversation_id,message_type,idempotency_key,outcome,reasons) "
                    "VALUES ('2026-10-14T00:00:00+00:00','sideshift:U1','sideshift','r','x','k','sent','[]')")
        old.close()
        accepted_mutation = []
        class ObserveMigration(Journal):
            def _migrate(inner):
                super()._migrate()
                observer = sqlite3.connect(path)
                try:
                    observer.execute("UPDATE decisions SET outcome='error'")
                    observer.commit()
                    accepted_mutation.append(True)
                except sqlite3.IntegrityError:
                    pass
                finally:
                    observer.close()
        j = ObserveMigration(path)
        self.addCleanup(j.conn.close)
        self.assertEqual(accepted_mutation, [], 'Migration commits before recreating append-only triggers')

    def test_N20_bad_creator_name_does_not_abort_other_contracts(self):
        bad, good = self.contract(contractorName=42), self.contract(id='C2', contractorId='U2', contractorName='Bea')
        class Client:
            def pages(inner, path, **kw):
                return [bad, good] if path == '/contracts' else [
                    {'id': 'chat1', 'members': [flow.COMPANY, 'U1']}, {'id': 'chat2', 'members': [flow.COMPANY, 'U2']}]
        client = Client()
        class Source:
            def __init__(inner):
                inner.client = client
            def read(inner, chat, uids):
                return conv(invite(cid='C2' if chat == 'chat2' else 'C1', at=NOW), uid=uids[0], chat=chat)
        f = flow.Flow(client, Source(), None, self.j, lambda chat: ('route', 'person'), now=lambda: NOW)
        _, error = self.no_crash(f.run)
        seen = [e['ref'] for e in self.j.events('sideshift:U2')]
        self.assertIn('C2', seen, error)

    def test_N21_known_seed_recipient_can_change_display_name(self):
        uid = next(iter(seed_journal.PRE_GATE_EMAIL_ASKS))
        with patch.object(seed_journal, 'OLD', self.root / 'missing.json'):
            seed_journal.seed(self.j, [self.contract(contractorId=uid, contractorName='Changed Display Name')])
        self.assertTrue(self.j.spent(f'gate:ask-app-email:sideshift:{uid}'), 'Stable known recipient is discarded on rename')

    def test_N21_null_legacy_reminders_does_not_starve_valid_seeds(self):
        p = self.root / 'old.json'
        p.write_text(json.dumps({'C1': {'reminders': None}, 'C2': {'reminders': [{'n': 0}]}}))
        with patch.object(seed_journal, 'OLD', p):
            _, error = self.no_crash(lambda: seed_journal.seed(self.j, [self.contract(), self.contract(id='C2')]))
        self.assertTrue(self.j.spent('gate:contract-reminder-1:sideshift:U1:C2'), error)

    def test_N21_unattributed_legacy_attempt_holds_instead_of_permitting_repeat(self):
        p = self.root / 'old.json'
        p.write_text(json.dumps({'C1': {'reminders': [{'n': 'unreadable'}]}}))
        with patch.object(seed_journal, 'OLD', p):
            seed_journal.seed(self.j, [self.contract()])
        from gate import policy
        t = replace(policy.load()['contract-reminder-1'], approved='2026-10-14')
        sender = Sender()
        self.gate(sender=sender, types={t.id: t}).run(self.action(message_type=t.id, fields={'First': 'Ada'}))
        self.assertEqual(sender.calls, [], 'Printed warning leaves both possible delivered reminder keys eligible')

    def test_N22_withdrawal_binds_contract_owner_to_creator(self):
        calls = []
        class Writer:
            def request(inner, *a, **kw):
                calls.append((a, kw))
        old = conv(invite(at=NOW - timedelta(hours=40)))
        withdraw.withdraw('C1', lambda cid: self.contract(contractorId='OTHER'), lambda: old,
                          self.j, 'sideshift:U1', NOW, Writer())
        self.assertEqual(calls, [], 'Irreversible rejection uses an unrelated creator chat to establish inactivity')

    def test_N22_uncertain_withdrawal_is_not_retried_automatically(self):
        calls = []
        class Writer:
            def request(inner, *a, **kw):
                calls.append((a, kw))
                raise TimeoutError('request may have left')
        for _ in range(2):
            withdraw.withdraw('C1', lambda cid: self.contract(), lambda: conv(invite(at=NOW - timedelta(hours=40))),
                              self.j, 'sideshift:U1', NOW, Writer(), lambda: [])   # adapted: explicit empty requests (S02)
        self.assertEqual(len(calls), 1, 'withdraw-uncertain is recorded but never consulted')

    def test_N22_withdrawal_uses_answer_and_attachment_review_facts(self):
        # adapted 2026-10-15: marks carry a content fingerprint (review N12 requires that), via checks.mark
        q = msg('q', 'What do I do?', at=NOW - timedelta(hours=49), direction=IN, attachments=1)
        self.j.event('sideshift:U1', 'answered', checks.mark(q), {'by': 'captain'})
        self.j.event('sideshift:U1', 'attachment-reviewed', checks.mark(q), {'by': 'captain'})
        c = conv(invite(at=NOW - timedelta(hours=50)), q)
        reasons = withdraw.blockers(self.contract(), c, NOW, self.j.events('sideshift:U1'), True)
        self.assertEqual(reasons, [], 'Explicit captain resolution is ignored, so this invite can never clear')
