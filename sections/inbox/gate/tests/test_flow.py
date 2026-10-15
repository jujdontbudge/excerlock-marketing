"""The contract flow decides; the gate sends. Fakes only."""
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import flow as F  # noqa: E402
from gate.handles import Profile  # noqa: E402
from gate.journal import Journal  # noqa: E402
from gate.model import IN, OUT, Conversation, Decision, Msg  # noqa: E402

INVITED = datetime(2026, 10, 14, 14, 0, tzinfo=timezone.utc)


class Pages:
    def __init__(self, items):
        self.items = items

    def request(self, method, path, **kw):
        return {'data': next(i for i in self.items if path.endswith(i['id']))}

    def pages(self, path, **kw):
        return list(self.items)


class FakeLive:
    def __init__(self, conversations, chats):
        self.client, self.chats = Pages(conversations), chats

    def read(self, chat_id, members=None):
        return self.chats[chat_id]


class RecordingGate:
    def __init__(self):
        self.actions = []

    def run(self, action):
        self.actions.append(action)
        return Decision('held', ['fake gate'])


GUIDE = Msg('g', '2026-10-14T14:00:02Z', OUT, 'company', 'Warm-up: https://docs.google.com/document/d/1guNLxDR65XXBlYbMOgHIeUw_aRi8cT8J3fSS71vNIEY/edit', 'text')


def chat(*extra):
    msgs = (Msg('i', '2026-10-14T14:00:00Z', OUT, 'company', 'https://app.sideshift.app/campaign-invite/C1?programId=P', 'invite_link'), GUIDE) + extra
    return Conversation('sideshift', 'chat1', ('U1',), msgs, 'fp', '')


ACCEPT = Msg('h', '2026-10-14T15:00:00Z', IN, 'creator', '📨 Requested 2 handles: @k_new (tiktok), @k_new (instagram) for this contract.', 'handle_request')


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.journal = Journal(Path(self.tmp.name) / 'g.db')
        self.fetched = []

    def tearDown(self):
        self.tmp.cleanup()

    def flow(self, contract, conv, hours, conversations=None):
        gate = RecordingGate()
        fetch = lambda p: (lambda h: self.fetched.append((p, h)) or Profile(p, h, True, INVITED, 0, 0))
        f = F.Flow(Pages([contract]), FakeLive(conversations or [{'id': 'chat1', 'members': [F.COMPANY, 'U1']}], {'chat1': conv}),
                   gate, self.journal, lambda chat_id: ('c1', 'p1'), now=lambda: INVITED + timedelta(hours=hours),
                   fetchers={'tiktok': fetch('tiktok'), 'instagram': fetch('instagram')},
                   read_client=Pages([]))   # adapted 2026-10-15: no reader means unknown requests (review S02)
        return f, gate

    def contract(self, status='pending'):
        # adapted 2026-10-15 (review AB01): real contracts always carry createdAt (checked live); Flow uses it to
        # place a request before any chat read
        return {'id': 'C1', 'contractorId': 'U1', 'contractorName': 'Kamila Rueda', 'status': status,
                'createdAt': INVITED.isoformat()}

    def types(self, gate):
        return [a.message_type for a in gate.actions]

    def test_reminder_schedule(self):
        for hours, expected in ((5, []), (6, ['contract-reminder-1']), (11.9, ['contract-reminder-1']),
                                (12, ['contract-reminder-2']), (35.9, ['contract-reminder-2']), (36, [])):
            f, gate = self.flow(self.contract(), chat(), hours)
            f.run()
            self.assertEqual(self.types(gate), expected, hours)

    def test_reminder_uses_her_first_name(self):
        f, gate = self.flow(self.contract(), chat(), 7)
        f.run()
        self.assertEqual(gate.actions[0].fields, {'First': 'Kamila'})

    def test_withdraw_due_is_recorded_once_and_sends_nothing(self):
        for _ in range(2):
            f, gate = self.flow(self.contract(), chat(), 40)
            out = f.run()
            self.assertEqual(gate.actions, [])
        kinds = [e['kind'] for e in self.journal.events('sideshift:U1')]
        self.assertEqual(kinds.count('withdraw-due'), 1)
        self.assertIn('withdraw-held', kinds)   # no write key in tests: it records why and does nothing

    def test_handle_request_while_pending_checks_handles_once_and_sends_nothing(self):
        # A chat handle request is only "maybe signed": it stops reminders, but onboarding waits for the active contract.
        for _ in range(2):
            f, gate = self.flow(self.contract(), chat(ACCEPT), 7)
            f.run()
            self.assertEqual(self.types(gate), [])
        self.assertEqual(self.fetched, [('tiktok', 'k_new'), ('instagram', 'k_new')])
        check = [e for e in self.journal.events('sideshift:U1') if e['kind'] == 'handle-check']
        self.assertEqual(len(check), 1)
        self.assertIn('"verdict": "pass"', check[0]['data'])

    def test_signed_without_guide_gets_the_guide_first(self):
        # 2026-10-15: Kamila signed after the old warm-up bot was retired and never got the promised guide.
        f, gate = self.flow(self.contract('active'), Conversation('sideshift', 'chat1', ('U1',), (ACCEPT,), 'fp', ''), 2)
        f.run()
        self.assertEqual(self.types(gate), ['warmup-guide'])

    def test_accepted_never_gets_a_reminder_even_after_36h(self):
        f, gate = self.flow(self.contract(), chat(ACCEPT), 40)
        f.run()
        self.assertEqual(self.types(gate), [])
        self.assertNotIn('withdraw-due', [e['kind'] for e in self.journal.events('sideshift:U1')])

    def test_active_contract_asks_for_email(self):
        f, gate = self.flow(self.contract('active'), chat(), 2)
        f.run()
        self.assertEqual(self.types(gate), ['ask-app-email'])

    def test_closed_contracts_do_nothing(self):
        for status in ('rejected', 'cancelled', 'declined'):
            f, gate = self.flow(self.contract(status), chat(), 7)
            f.run()
            self.assertEqual(gate.actions, [])

    def test_two_chats_for_one_creator_never_guess(self):
        f, gate = self.flow(self.contract(), chat(), 7, conversations=[{'id': 'chat1', 'members': [F.COMPANY, 'U1']},
                                                                      {'id': 'chat2', 'members': [F.COMPANY, 'U1']}])
        out = f.run()
        self.assertEqual(gate.actions, [])
        self.assertIn('2 SideShift chats', out[0])


if __name__ == '__main__':
    unittest.main()


class StructuredRequests(FlowTests):
    def flow_with_apps(self, apps, conv, hours, contract=None):
        f, gate = self.flow(contract or self.contract(), conv, hours)
        f.read_client = Pages(apps)
        return f, gate

    def app(self, **kw):
        a = {'programId': F.CAMPAIGN, 'status': 'pending', 'platform': 'tiktok', 'handle': '@k_new', 'requestId': 'r1',
             'requestedAt': '2026-10-14T15:00:00Z', 'creator': {'id': 'U1'}}
        a.update(kw)
        return a

    def test_sideshift_request_blocks_reminders_without_any_chat_notice(self):
        f, gate = self.flow_with_apps([self.app(), self.app(platform='instagram', requestId='r2')], chat(), 7)
        f.run()
        self.assertEqual(self.types(gate), [])
        checks_ = [e for e in self.journal.events('sideshift:U1') if e['kind'] == 'handle-check']
        self.assertEqual(len(checks_), 1)
        self.assertIn('"tiktok": "k_new"', checks_[0]['data'])

    def test_requests_from_other_campaigns_creators_or_before_the_invite_do_not_count(self):
        # adapted 2026-10-15 (review V04): a rejected request is still evidence she requested handles, so it blocks
        for app in (self.app(programId='OTHER'), self.app(creator={'id': 'U2'}), self.app(requestedAt='2026-10-01T00:00:00Z'),
                    self.app(isJoinRequest=True)):
            f, gate = self.flow_with_apps([app], chat(), 7)
            f.run()
            self.assertEqual(self.types(gate), ['contract-reminder-1'], app)

    def test_unreadable_requests_fall_back_to_chat_signals(self):
        class Broken:
            def pages(self, *a, **k):
                raise RuntimeError('HTTP503')
        f, gate = self.flow(self.contract(), chat(ACCEPT), 7)
        f.read_client = Broken()
        out = f.run()
        self.assertEqual(self.types(gate), [])
        self.assertTrue(any('could not be read' in line for line in out))
