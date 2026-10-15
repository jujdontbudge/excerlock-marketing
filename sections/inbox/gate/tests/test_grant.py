"""Free-Premium grants: check first, grant once, never retry blindly (excerlock-access skill rules)."""
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import grant as G  # noqa: E402
from gate.journal import Journal  # noqa: E402


class Runner:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []

    def __call__(self, args, **kw):
        self.calls.append(args[1:3])
        return SimpleNamespace(stdout=self.replies.pop(0), stderr='')


class Grants(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.j = Journal(Path(self.tmp.name) / 'g.db')

    def tearDown(self):
        self.tmp.cleanup()

    def test_check_then_grant_then_recorded(self):
        r = Runner(['NONE: kamila@gmail.com has no active free Premium.', 'GRANTED: kamila@gmail.com has free ExcerLock Premium with no end date.'])
        ok, line = G.grant(self.j, 'k', 'Kamila@Gmail.com', 'UGC @kamila_walks', r)
        self.assertTrue(ok)
        self.assertEqual(r.calls, [['check', 'kamila@gmail.com'], ['grant', 'kamila@gmail.com']])
        self.assertTrue(self.j.premium_granted('k', 'kamila@gmail.com'))

    def test_already_active_is_not_granted_again(self):
        r = Runner(['ACTIVE: kamila@gmail.com has free Premium with no end date.'])
        self.assertTrue(G.grant(self.j, 'k', 'kamila@gmail.com', 'n', r)[0])
        self.assertEqual(r.calls, [['check', 'kamila@gmail.com']])

    def test_unclear_grant_is_checked_never_repeated(self):
        r = Runner(['NONE: kamila@gmail.com has no active free Premium.', 'ERROR: Server error (502). Nothing was confirmed; run check before retrying.', 'NONE: kamila@gmail.com has no active free Premium.'])
        ok, _ = G.grant(self.j, 'k', 'kamila@gmail.com', 'n', r)
        self.assertFalse(ok)
        self.assertEqual([c[0] for c in r.calls], ['check', 'grant', 'check'])
        self.assertFalse(self.j.premium_granted('k', 'kamila@gmail.com'))

    def test_bad_email_or_broken_check_does_nothing(self):
        self.assertFalse(G.grant(self.j, 'k', 'kamila at gmail', 'n', Runner([]))[0])
        r = Runner(['ERROR: The access token was rejected. Ask Johan to re-enable it.'])
        self.assertFalse(G.grant(self.j, 'k', 'kamila@gmail.com', 'n', r)[0])
        self.assertEqual(r.calls, [['check', 'kamila@gmail.com']])


if __name__ == '__main__':
    unittest.main()
