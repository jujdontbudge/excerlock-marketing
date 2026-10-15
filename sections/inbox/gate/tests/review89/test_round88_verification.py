"""Round-88 reproductions and ownership controls against the current snapshot."""
from types import SimpleNamespace

from gate.tests.review88 import test_round88 as previous
from gate.tests.review3 import support
import grant


class Round88Verification(previous.PremiumRecipientRetry):
    # Inherit all seven original assertions without changing their expectations.
    def test_legacy_receipt_alone_blocks_different_recipient(self):
        self.configure(replace_during_grant=False)
        self.j.event('sideshift:U1', 'premium-granted', 'LEGACY@example.com',
                     {'email': 'legacy@example.com', 'result': 'GRANTED: legacy@example.com'})
        d = self.run_access('original@example.com')
        self.assertEqual(d.outcome, 'held', d)
        self.assertIn('another email', str(d.reasons))
        self.assertEqual(self.commands, [])
        self.assertEqual(self.grants, [])
        self.assertEqual(self.deliveries, [])

    def test_competing_email_claim_during_check_is_rechecked_transactionally(self):
        self.configure(replace_during_grant=False)
        other = self.new_journal(self.root / 'shared.db')
        original_runner = self.runner

        def runner(argv, **kwargs):
            if argv[1] == 'check':
                self.assertEqual(other.settle_premium('sideshift:U1', 'competing@example.com', False), 'ok')
            return original_runner(argv, **kwargs)

        worker = self.workers['U1']
        worker.gate.granter = lambda a: grant.grant(worker.journal, a.creator_key,
            a.fields['email'], 'offline review', runner=runner)
        d = self.run_access('original@example.com')
        self.assertEqual(d.outcome, 'held', d)
        self.assertIn('original@example.com:other-email', self.j.flags('sideshift:U1', 'grant-error'))
        self.assertEqual(self.grants, [])
        self.assertEqual(self.deliveries, [])
        self.assertEqual(self.j.creator_premium_emails('sideshift:U1'), {'competing@example.com'})

    def test_same_email_unresolved_none_is_not_blindly_regranted(self):
        self.configure(replace_during_grant=False)
        self.j.claim_grant('sideshift:U1', 'original@example.com')
        d = self.run_access('original@example.com')
        self.assertEqual(d.outcome, 'held', d)
        self.assertIn('never confirmed', str(d.reasons))
        self.assertEqual(self.commands, [('check', 'original@example.com')])
        self.assertEqual(self.grants, [])


class PremiumRecordCoverage(support.Case):
    def test_all_three_record_shapes_reserve_creator_recipient(self):
        for kind in ('premium-granted', 'premium-acknowledged', 'grant-intent'):
            with self.subTest(kind=kind):
                j = self.new_journal()
                if kind == 'premium-granted':
                    j.event('sideshift:U1', kind, 'OLD@example.com', {'email': 'old@example.com'})
                else:
                    j.event('premium:old@example.com', kind, 'old@example.com', {'by': 'sideshift:U1'})
                self.assertEqual(j.creator_premium_emails('sideshift:U1'), {'old@example.com'})
                self.assertEqual(j.settle_premium('sideshift:U1', 'new@example.com', False), 'other-email')
                self.assertEqual(j.settle_premium('sideshift:U1', 'new@example.com', True), 'other-email')
                self.assertEqual(j.premium_owners('new@example.com'), set())

    def test_legacy_same_address_active_remains_read_only_confirmation(self):
        self.grant_receipt()
        commands = []

        def runner(argv, **kwargs):
            commands.append(argv[1:3])
            return SimpleNamespace(returncode=0, stdout='ACTIVE: ada@example.com', stderr='')

        ok, line = grant.grant(self.j, 'sideshift:U1', 'ada@example.com', 'offline review', runner=runner)
        self.assertTrue(ok, line)
        self.assertEqual(commands, [['check', 'ada@example.com']])
