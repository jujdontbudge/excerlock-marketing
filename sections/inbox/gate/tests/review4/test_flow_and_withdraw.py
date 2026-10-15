from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from gate import checks
from gate.model import IN
from .support import Case, NOW, Live, conv, flow, handles, invite, msg, withdraw


class WithdrawBoundaries(Case):
    def old_chat(self):
        return conv(invite(at=NOW - timedelta(hours=40)))

    def test_R15_withdrawal_checks_requested_contract_identity(self):
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)))
        withdraw.withdraw('C1', lambda cid: self.contract(id='OTHER'),
                          lambda: conv(invite(cid='OTHER', at=NOW - timedelta(hours=40))),
                          self.j, 'sideshift:U1', NOW, writer)
        self.assertEqual(writes, [], 'GET returns OTHER but the code rejects requested C1 using OTHER evidence')

    def test_R15_withdrawal_has_durable_intent_before_post(self):
        calls = []
        class Crash(BaseException):
            pass
        def request(*a, **kw):
            calls.append((a, kw))
            if len(calls) == 1:
                raise Crash('process died after request left')
        writer = SimpleNamespace(request=request)
        with self.assertRaises(Crash):
            withdraw.withdraw('C1', lambda cid: self.contract(), self.old_chat, self.j, 'sideshift:U1', NOW, writer, lambda: [])
        withdraw.withdraw('C1', lambda cid: self.contract(), self.old_chat, self.j, 'sideshift:U1', NOW, writer, lambda: [])
        self.assertEqual(len(calls), 1, 'No intent exists to block a replay after a process death')

    def test_R15_overlapping_withdrawals_have_one_owner(self):
        calls = []
        def request(*a, **kw):
            calls.append((a, kw))
            if len(calls) == 1:
                withdraw.withdraw('C1', lambda cid: self.contract(), self.old_chat,
                                  self.j, 'sideshift:U1', NOW, writer, lambda: [])
        writer = SimpleNamespace(request=request)
        withdraw.withdraw('C1', lambda cid: self.contract(), self.old_chat, self.j, 'sideshift:U1', NOW, writer, lambda: [])
        self.assertEqual(len(calls), 1, 'Terminal event deduplication does not deduplicate the POSTs')

    def test_R15_failed_response_is_not_recorded_as_confirmed_withdrawal(self):
        writer = SimpleNamespace(request=lambda *a, **kw: {'status': 'failed', 'error': 'not rejected'})
        result = withdraw.withdraw('C1', lambda cid: self.contract(), self.old_chat, self.j, 'sideshift:U1', NOW, writer)
        self.assertNotEqual(result[0], 'withdrawn', 'Any nonthrowing response is treated as irreversible success')

    def test_R16_old_handle_approval_cannot_withdraw_a_new_invite_at_one_hour(self):
        c = conv(invite('old', at=NOW - timedelta(hours=50)),
                 msg('approval', '✅ Your handle @old (tiktok) was approved for this contract.', at=NOW - timedelta(hours=49)),
                 invite('genuine-new-invite', at=NOW - timedelta(hours=1)))
        writes = []
        withdraw.withdraw('C1', lambda cid: self.contract(), lambda: c, self.j, 'sideshift:U1', NOW,
                          SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw))))
        self.assertEqual(writes, [], 'Sticky approved_since_round makes every future invite a repost')


class StructuredApplications(Case):
    def app(self, **kw):
        return dict(id='app1', requestId='req1', status='pending', programId=flow.CAMPAIGN,
                    creator={'id': 'U1'}, platform='tiktok', handle='new', requestedAt=NOW.isoformat(), **kw)

    def test_R07_application_read_failure_cannot_enable_withdrawal(self):
        writes = []
        class Client:
            def pages(inner, path, **kw):
                return [self.contract()]
            def request(inner, *a, **kw):
                return self.contract()
        source = Live(conv(invite(at=NOW - timedelta(hours=40))))
        source.client = SimpleNamespace(pages=lambda path: [{'id': 'chat1', 'members': [flow.COMPANY, 'U1']}])
        def unavailable(*a, **kw):
            raise TimeoutError('authoritative handle requests unavailable')
        f = flow.Flow(Client(), source, None, self.j, lambda chat: ('route1', 'person1'), now=lambda: NOW,
                      read_client=SimpleNamespace(pages=unavailable),
                      write_client=SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw))))
        f.run()
        self.assertEqual(writes, [], 'Unknown application coverage becomes an empty list and enables rejection')

    def test_R07_applications_created_after_flow_read_are_rechecked_for_withdrawal(self):
        reads, writes = [], []
        class Client:
            def pages(inner, path, **kw):
                return [self.contract()]
            def request(inner, *a, **kw):
                return self.contract()
        source = Live(conv(invite(at=NOW - timedelta(hours=40))))
        source.client = SimpleNamespace(pages=lambda path: [{'id': 'chat1', 'members': [flow.COMPANY, 'U1']}])
        def applications(path):
            reads.append(path)
            return [] if len(reads) == 1 else [self.app()]
        f = flow.Flow(Client(), source, None, self.j, lambda chat: ('route1', 'person1'), now=lambda: NOW,
                      read_client=SimpleNamespace(pages=applications),
                      write_client=SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw))))
        f.run()
        self.assertEqual(writes, [], f'Only {len(reads)} application read, before the fresh contract/chat checks')

    def test_R17_edit_to_structured_handle_record_is_checked_again(self):
        fetched = []
        def fetch(h):
            fetched.append(h)
            return handles.Profile('tiktok', h, True, NOW, 0, 0)
        f = flow.Flow(None, None, None, self.j, None, now=lambda: NOW, fetchers={'tiktok': fetch})
        app = self.app()
        f.check_handles('sideshift:U1', conv(invite()), self.contract(applications=[app]))
        app['handle'] = 'replacement_ugc'
        f.check_handles('sideshift:U1', conv(invite()), self.contract(applications=[app]))
        self.assertIn('replacement_ugc', fetched, 'apps:requestId does not identify the reviewed handle revision')

    def test_R17_partial_profile_data_is_not_permanently_finished(self):
        fetched = []
        def fetch(h):
            fetched.append(h)
            return handles.Profile('tiktok', h, True, None if len(fetched) == 1 else NOW, 0, 0)
        f = flow.Flow(None, None, None, self.j, None, now=lambda: NOW, fetchers={'tiktok': fetch})
        c = self.contract(applications=[self.app()])
        f.check_handles('sideshift:U1', conv(invite()), c)
        f.check_handles('sideshift:U1', conv(invite()), c)
        self.assertEqual(len(fetched), 2, 'exists=True with transient missing creation data is still consumed forever')

    def test_R18_null_contract_row_does_not_starve_next_creator(self):
        good = self.contract(id='C2', contractorId='U2')
        class Client:
            def pages(inner, path, **kw):
                return [None, good]
        source = Live(conv(invite('i2', cid='C2', at=NOW), uid='U2', chat='chat2'))
        source.client = SimpleNamespace(pages=lambda path: [{'id': 'chat2', 'members': [flow.COMPANY, 'U2']}])
        f = flow.Flow(Client(), source, None, self.j, lambda chat: ('route2', 'person2'), now=lambda: NOW)
        _, error = self.no_crash(f.run)
        self.assertTrue(self.j.events('sideshift:U2'), f'Contract .get() remains outside isolation: {error}')
