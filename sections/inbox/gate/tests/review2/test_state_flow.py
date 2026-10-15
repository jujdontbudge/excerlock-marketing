"""Contract correlation, scheduler failure recovery, malformed provider data, and migration."""
from dataclasses import replace
from datetime import timedelta
from unittest.mock import patch

from gate import checks
from gate.live import LiveReadError, SideShiftLive
from gate.model import IN, OUT
from .support import (Case, NOW, Pages, RawClient, StaticLive, checks, conversation,
                               flow, handles, invite, message, raw, request, seed_module)


class AcceptanceDefects(Case):
    def test_G09_other_contract_request_accepts_this_contract(self):
        c = conversation(invite('C1'), invite('C2', id='i2'), request())
        self.assertFalse(checks.accepted(c, self.contract(id='C1')),
                         'Unbound request after two invitations cannot positively sign both')

    def test_G09_no_matching_invite_accepts_any_old_request(self):
        self.assertFalse(checks.accepted(conversation(request()), self.contract(id='C2')))

    def test_G09_deleted_request_is_acceptance(self):
        self.assertFalse(checks.accepted(conversation(invite(), request(deleted=True)), self.contract()))

    def test_G09_creator_can_type_a_system_request(self):
        # classify() has only content, with no structured application/event provenance.
        self.assertFalse(checks.accepted(conversation(invite(), request()), self.contract()),
                         'Ordinary creator-authored text alone must not positively establish signing')

    def test_G10_reinvite_uses_first_invitation(self):
        old = invite(id='old', at='2026-10-01T10:00:00Z')
        new = invite(id='new', at='2026-10-14T15:00:00Z')
        self.assertEqual(checks.invite_time(conversation(old, new), self.contract()),
                         checks.ts(new.at))

    def test_G10_reinvite_reuses_old_acceptance(self):
        c = conversation(invite(id='old', at='2026-10-01T10:00:00Z'),
                         request(at='2026-10-01T11:00:00Z'),
                         invite(id='new', at='2026-10-14T15:00:00Z'))
        self.assertFalse(checks.accepted(c, self.contract()))

    def test_G10_new_invite_generation_reuses_spent_operation_key(self):
        g = self.gate()
        old = self.action(contract=self.contract(inviteGeneration='old'))
        new = self.action(contract=self.contract(inviteGeneration='new'))
        self.assertNotEqual(g.key(self.type, old), g.key(self.type, new))

    def test_G10_substring_contract_match_starts_wrong_clock(self):
        self.assertIsNone(checks.invite_time(conversation(invite('C10')), self.contract(id='C1')))

    def test_G10_inbound_link_is_not_verified_invite_delivery(self):
        self.assertIsNone(checks.invite_time(conversation(invite(direction=IN)), self.contract()))

    def test_G10_object_created_time_is_not_invite_time(self):
        self.assertIsNone(checks.invite_time(conversation(), self.contract(createdAt=NOW.timestamp() - 864000)))

    def test_G11_terminal_contract_is_not_onboarding_eligible(self):
        for status in ('expired', 'ended', 'completed'):
            with self.subTest(status=status):
                f = self.flow(contract=self.contract(status=status))
                f.run()
                self.assertEqual(self.recorder.actions, [])

    def test_G11_cancelled_with_old_request_is_not_welcomed(self):
        f = self.flow(contract=self.contract(status='cancelled'), conv=conversation(invite(), request()))
        f.run()
        self.assertEqual(self.recorder.actions, [])

    def test_G11_contract_is_never_refreshed_during_review(self):
        # Separate live contract changes: the Action snapshot remains pending, chat stays identical.
        current = self.contract()
        def reviewer(*a):
            current['status'] = 'active'
            return 'SEND', 'old chat', []
        g = self.gate(reviewer=reviewer)
        g.contract_reader = lambda cid: dict(current)   # adapted 2026-10-15: production gates are built with a reader
        g.run(self.action(contract=dict(current)))
        self.assertEqual(g.sender.calls, [], 'Gate has no current-contract/application reader')


class FlowDefects(Case):
    def test_G22_fractional_timestamp_sorts_before_earlier_whole_second(self):
        rows = [raw(id='out', createdAt='2026-10-14T05:00:00Z', content='Hello'),
                raw(id='question', senderUserId='U1', createdAt='2026-10-14T05:00:00.100Z', content='What do I upload?')]
        c = SideShiftLive(RawClient(rows), 'COMPANY').read('chat1')
        self.assertEqual([m.id for m in checks.unanswered(c)], ['question'])

    def test_G19_handle_fetch_failure_is_never_retried(self):
        attempts = []
        def fail(h):
            attempts.append(h)
            raise ValueError('malformed profile')
        # adapted 2026-10-15 (review BK02): every requested platform needs a checker, or the batch is 'ask'
        f = self.flow(conv=conversation(invite(), request()), fetchers={'tiktok': fail, 'instagram': fail})
        try:
            f.run()
        except ValueError:
            pass
        f.run()
        self.assertEqual(len(attempts), 2, 'accepted event commits before fetch and suppresses all future checks')

    def test_G19_replacement_handle_request_is_not_checked(self):
        seen = []
        fetchers = {p: (lambda h, p=p: seen.append((p, h)) or handles.Profile(p, h, True, NOW, 0, 0))
                    for p in ('tiktok', 'instagram')}
        f = self.flow(conv=conversation(invite(), request()), fetchers=fetchers)
        f.run()
        f.live.conv = conversation(invite(), request(), replace(request(), id='h2', text=request().text.replace('@new', '@replacement')))
        f.run()
        self.assertIn(('tiktok', 'replacement'), seen)

    def test_G20_missing_metrics_or_future_creation_passes_newness(self):
        for date, posts, followers in ((NOW, None, None), (NOW + timedelta(days=1), 0, 0)):
            with self.subTest(date=date, posts=posts):
                p = {'tiktok': handles.Profile('tiktok', 'new', True, date, posts, followers),
                     'instagram': handles.Profile('instagram', 'new', True, None, posts, followers)}
                self.assertNotEqual(handles.judge(p, NOW)[0], 'pass')

    def test_G21_late_second_reminder_promises_one_more_day(self):
        self.clock = NOW + timedelta(hours=35)  # use an invitation precisely 35h old
        c = conversation(invite(at=NOW.isoformat()))
        from gate import policy
        f = self.flow(conv=c, gate=self.gate(conv=c, types_=policy.load()))
        f.run()
        text = ' '.join(row['text'] or '' for row in self.journal.history('sideshift:U1'))
        self.assertNotIn('about one more day', text, 'Only 1h remains in the actual rendered proposal')

    def test_G25_malformed_live_message_is_translated_to_hold(self):
        error = None
        try:
            SideShiftLive(RawClient([raw(attachmentCount='unknown')]), 'COMPANY').read('chat1')
        except LiveReadError:
            pass
        except Exception as exc:
            error = exc
        self.assertIsNone(error, f'Normalization escaped live-read error boundary: {error}')

    def test_G25_one_bad_contract_starves_later_creators(self):
        bad = self.contract(id='bad', createdAt=10**30)
        good = self.contract(id='C2')
        f = self.flow()
        f.contracts_client = Pages([bad, good])
        f.live.conv = conversation()  # overflow in fallback time on first item
        try:
            f.run()
        except (ValueError, OverflowError, OSError):
            pass
        observed = [e['ref'] for e in self.journal.events('sideshift:U1')]
        self.assertIn('C2', observed)

    def test_G01_duplicate_contacts_routes_do_not_choose_last(self):
        class Contacts:
            def call(self, name, args):
                if name == 'list_conversations':
                    return [{'id': 'route1', 'external_id': 'sideshift:chat1'},
                            {'id': 'route2', 'external_id': 'sideshift:chat1'}]
                return {'participants': [{'person_id': 'wrong-human'}]}
        self.assertEqual(flow.contacts_routes(Contacts())('chat1'), (None, None))


class SeedDefects(Case):
    def test_G23_old_unconfirmed_reminder_is_promoted_to_sent(self):
        state = self.root / 'old.json'
        state.write_text('{"C1":{"reminders":[{"n":0,"error":"timeout"}]}}')
        with patch.object(seed_module, 'OLD', state):
            seed_module.seed(self.journal, [self.contract()])
        rows = self.journal.history('sideshift:U1')
        self.assertFalse(any(r['outcome'] == 'sent' for r in rows), 'Legacy attempt is not delivery proof')

    def test_G23_name_only_seed_can_consume_wrong_human(self):
        with patch.object(seed_module, 'OLD', self.root / 'absent'):
            seed_module.seed(self.journal, [self.contract(contractorName='Jillian Collins', contractorId='NEW-SAME-NAME')])
        self.assertFalse(self.journal.spent('gate:ask-app-email:sideshift:NEW-SAME-NAME'))

    def test_G23_malformed_legacy_row_aborts_migration(self):
        state = self.root / 'old.json'
        state.write_text('{"C1":{"reminders":[{"n":"bad"},{"n":1}]}}')
        error = None
        with patch.object(seed_module, 'OLD', state):
            try:
                seed_module.seed(self.journal, [self.contract()])
            except TypeError as exc:
                error = exc
        self.assertIsNone(error, 'A malformed row aborts all subsequent evidence import')
