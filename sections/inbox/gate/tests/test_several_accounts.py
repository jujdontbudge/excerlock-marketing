"""A creator with more than one SideShift account linked to her is handled by the captain: the gate holds every
send and grant, and withdrawal holds (review CU01-CU03; live 2026-10-15: 0 of 7 people)."""
import unittest
from types import SimpleNamespace

from gate.tests.review4.support import Case, NOW, conv, invite, policy, withdraw
from datetime import timedelta


class SeveralAccounts(Case):
    def link(self, *accounts):
        for a in accounts:
            self.j.link_person('person1', a)

    def test_single_account_is_not_held_by_this_rule(self):
        self.link('sideshift:U1')
        self.assertEqual(self.gate()._several_accounts(self.action()), [])

    def test_a_second_linked_account_holds_every_send(self):
        self.link('sideshift:U1', 'sideshift:U2')
        d = self.gate().run(self.action())
        self.assertEqual(d.outcome, 'held')
        self.assertTrue(any('other linked SideShift accounts' in r for r in d.reasons), d.reasons)

    def test_a_second_linked_account_holds_withdrawal(self):
        self.link('sideshift:U1', 'sideshift:U2')
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append(1) or {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        result = withdraw.withdraw('C1', lambda cid: self.contract(), lambda: conv(invite(at=NOW - timedelta(hours=40))),
                                   self.j, 'sideshift:U1', NOW, writer, lambda: [])
        self.assertEqual(writes, [])
        self.assertEqual(result[0], 'held')


if __name__ == '__main__':
    unittest.main()
