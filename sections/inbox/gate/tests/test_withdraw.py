"""Withdrawal is irreversible: every blocker must be absent, checked fresh."""
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import withdraw as W  # noqa: E402
from gate.journal import Journal  # noqa: E402
from gate.model import IN, OUT, Conversation, Msg  # noqa: E402

INV = datetime(2026, 10, 14, 5, 0, tzinfo=timezone.utc)
LINK = Msg('i', '2026-10-14T05:00:00Z', OUT, 'company', 'https://app.sideshift.app/campaign-invite/C1?x', 'invite_link')
TEXT = Msg('t', '2026-10-14T05:00:01Z', OUT, 'company', "Here's your contract.", 'text')


def conv(*extra):
    return Conversation('sideshift', 'chat', ('U',), (LINK, TEXT) + extra, 'fp', '')


class Writer:
    def __init__(self, error=None):
        self.calls, self.error = [], error

    def request(self, method, path, payload=None, request_id=None):
        self.calls.append((method, path, request_id))
        if self.error:
            raise self.error
        return {'data': {'id': 'C1', 'status': 'rejected'}}


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.j = Journal(Path(self.tmp.name) / 'g.db')

    def tearDown(self):
        self.tmp.cleanup()

    def run_it(self, c, hours=37, status='pending', writer=None, events=()):
        for kind, ref in events:
            self.j.event('sideshift:U', kind, ref, {})
        self.writer = writer if writer is not None else Writer()
        return W.withdraw('C1', lambda cid: {'id': cid, 'status': status, 'contractorId': 'U'}, lambda: c, self.j, 'sideshift:U', INV + timedelta(hours=hours),
                          self.writer if writer is not False else None, lambda: [])   # adapted: explicit fresh, empty requests (S02)

    def test_clean_case_withdraws_once_silently(self):
        self.assertEqual(self.run_it(conv())[0], 'withdrawn')
        self.assertEqual(self.writer.calls, [('POST', '/contracts/C1/reject', 'withdraw-C1')])

    def test_dakota_case_recent_message_blocks(self):
        c = conv(Msg('d', (INV + timedelta(hours=21)).isoformat(), IN, 'creator', "i'm struggling to make a gmail", 'text'))
        outcome, reasons = self.run_it(c)
        self.assertEqual(outcome, 'held')
        self.assertTrue(any('last 24 hours' in r for r in reasons))
        self.assertEqual(self.writer.calls, [])

    def test_each_blocker(self):
        accepted = conv(Msg('h', '2026-10-14T06:00:00Z', IN, 'creator', '📨 Requested handle @x (instagram) for this contract.', 'handle_request'))
        cases = [dict(c=conv(), hours=35.9), dict(c=conv(), status='active'), dict(c=conv(), status='rejected'),
                 dict(c=accepted), dict(c=conv(), events=[('keep-invite', 'C1')]), dict(c=conv(), writer=False),
                 dict(c=conv(Msg('q', '2026-10-14T06:00:00Z', IN, 'creator', 'what do i film?', 'text')))]
        for kw in cases:
            self.setUp()
            self.assertEqual(self.run_it(**kw)[0], 'held', kw)

    def test_failed_call_is_uncertain_not_retried_silently(self):
        outcome, reasons = self.run_it(conv(), writer=Writer(error=TimeoutError()))
        self.assertEqual(outcome, 'held')
        self.assertIn('withdraw-uncertain', [e['kind'] for e in self.j.events('sideshift:U')])


if __name__ == '__main__':
    unittest.main()
