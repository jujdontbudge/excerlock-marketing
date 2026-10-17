"""The inbox never sends a reply by itself unless the captain turned INBOX_AUTO on (review CC01)."""
import unittest
from pathlib import Path
from unittest.mock import patch

import propose
from gate import policy


class InboxSwitch(unittest.TestCase):
    def test_default_makes_every_automatic_reply_a_draft(self):
        with patch.object(propose, 'INBOX_AUTO', Path('/nonexistent/INBOX_AUTO')):
            types = propose.inbox_types(policy.load())
        self.assertTrue(all(t.effective_mode != 'auto' for k, t in types.items() if k not in propose.AUTO_ALWAYS))   # adapted 2026-10-15: Premium always auto (captain)

    def test_switch_on_keeps_per_type_modes(self):
        loaded = policy.load()
        with patch.object(propose, 'INBOX_AUTO', Path(__file__)):
            types = propose.inbox_types(loaded)
        self.assertEqual({k: t.effective_mode for k, t in types.items()}, {k: t.effective_mode for k, t in loaded.items()})

    def test_flow_types_are_untouched(self):
        loaded = policy.load()
        with patch.object(propose, 'INBOX_AUTO', Path('/nonexistent/INBOX_AUTO')):
            propose.inbox_types(loaded)
        self.assertEqual(loaded['contract-reminder-1'].effective_mode, policy.load()['contract-reminder-1'].effective_mode)


if __name__ == '__main__':
    unittest.main()
