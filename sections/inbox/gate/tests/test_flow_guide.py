"""Captain, 2026-10-15: "send the warm-up guide with the contract always"."""
from types import SimpleNamespace

from gate.model import Conversation, Msg, OUT

from .test_flow import FlowTests as Base

INVITE_ONLY = Conversation('sideshift', 'chat1', ('U1',), (
    Msg('i', '2026-10-14T14:00:00Z', OUT, 'company', 'https://app.sideshift.app/campaign-invite/C1?programId=P', 'invite_link'),),
    'fp', '')


class GuideWithContract(Base):
    def flow_on(self, conv, hours, mode='auto'):
        f, gate = self.flow(self.contract(), conv, hours)
        gate.types = {'contract-invite': SimpleNamespace(effective_mode=mode)}
        return f, gate

    def test_fresh_invite_without_guide_gets_contract_message(self):
        f, gate = self.flow_on(INVITE_ONLY, 0.3)
        f.run()
        self.assertEqual(self.types(gate), ['contract-invite'])
        self.assertEqual(gate.actions[0].fields, {'First': 'Kamila', 'first': 'kamila'})

    def test_guide_already_sent_after_invite_is_not_repeated(self):
        from .test_flow import chat
        f, gate = self.flow_on(chat(), 0.3)
        f.run()
        self.assertEqual(self.types(gate), [])

    def test_switched_off_or_draft_sends_nothing(self):
        for mode in ('off', 'draft'):
            f, gate = self.flow_on(INVITE_ONLY, 0.3, mode)
            f.run()
            self.assertEqual(self.types(gate), [], mode)

    def test_older_invites_keep_their_reminders(self):
        f, gate = self.flow_on(INVITE_ONLY, 7)
        f.run()
        self.assertEqual(self.types(gate), ['contract-reminder-1'])
