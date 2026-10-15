"""Round 71's supplied eight tests, unchanged against the round-72 snapshot."""
import json
from datetime import timedelta

from gate import checks
from gate.live import to_msg
from gate.tests.review3.support import Case, NOW
from gate.tests.review71 import test_round71 as prior


class Round71Verification(prior.ContradictoryDeliveryClock):
    pass


class Round71JournalVerification(Case):
    def test_reused_clock_preserves_both_outbound_digests_and_id(self):
        row = dict(id='note', senderUserId='COMPANY',
                   createdAt=(NOW - timedelta(hours=10)).isoformat(), content='Old words')
        for text in ('Old words', 'New words'):
            row['content'] = text
            self.j.remember_notice('sideshift:U1', to_msg(row, 'COMPANY', 'Excerlock', ('U1',)))
        facts = [json.loads(e['data']) for e in self.j.events('sideshift:U1') if e['kind'] == 'out-seen']
        self.assertEqual({d['digest'] for d in facts},
                         {checks.text_digest('Old words'), checks.text_digest('New words')})
        self.assertEqual({d['id'] for d in facts}, {'note'})
        self.assertEqual(checks.changed_messages(self.j.events('sideshift:U1')), {'note'})

    def test_legacy_digest_without_id_is_never_proven_old(self):
        self.assertFalse(checks.before_round({'at': (NOW - timedelta(days=2)).isoformat(),
                                             'digest': checks.text_digest('Reminder')}, NOW))
