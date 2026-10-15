"""Offline Platform HTTP contract against the real creator intake/store/pipeline."""
import copy
import json
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'sections/creators'))
sys.path.insert(0, str(ROOT / 'sections/creators/tests'))
from creatorops.db import connect
from creatorops.pipeline import do_not_contact
from fakes import FakePlatform, Profile, Post
from adapter import Adapter, flags
from client import Client, APIError, RateLimited, MissingKey


def applicant(uid='u1', **kwargs):
    return {'userId': uid, 'name': 'Creator <script>', 'tiktok': '@creator', 'status': 'Waiting Review',
            'applicationAnswers': [
                {'requirementId': 'age', 'type': 'question', 'label': 'How old are you (age)?', 'value': '22'},
                {'requirementId': 'state', 'type': 'question', 'label': 'US state', 'value': 'Texas'},
                {'requirementId': 'camera', 'type': 'question', 'label': 'iPhone + second camera?', 'value': True},
                {'requirementId': 'walk', 'type': 'question', 'label': 'Treadmill + walks?', 'value': True},
                {'requirementId': 'video', 'type': 'video', 'label': 'Video', 'value': {'files': [{'url': 'https://example.com/video?a=1&b=2'}]}}
            ], **kwargs}


class Response:
    def __init__(self, data, status=200, headers=None):
        self.data, self.status_code, self.headers = data, status, headers or {}

    def json(self):
        return self.data


class HTTP:
    def __init__(self):
        self.applicants = [applicant()]
        self.calls = []
        self.failure = None
        self.ambiguous = False

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, copy.deepcopy(kwargs)))
        assert kwargs['headers']['x-api-key'] == 'test-secret'
        assert kwargs['allow_redirects'] is False
        if self.failure:
            return Response({'error': {'message': 'secret-private-data'}}, self.failure, {'Retry-After': '120'})
        path = url.split('/api/oauth/v1')[1]
        params = kwargs.get('params') or {}
        if path == '/applicants/overview':
            return Response({'data': {'totalJobs': 1, 'jobs': [{'id': 'j1'}]}})
        if path == '/jobs':
            return Response({'data': [{'id': 'j1', 'title': 'Job'}]})
        if path == '/jobs/j1':
            return Response({'data': {'id': 'j1', 'title': 'Job'}})
        if path in ('/applicants', '/applicants/advanced'):
            assert params['jobId'] == 'j1'
            data = copy.deepcopy(self.applicants)
            if params.get('cursor'):
                data = data[1:]
            return Response({'data': data[:1], 'hasMore': len(data) > 1, 'nextCursor': 'page2' if len(data) > 1 else None})
        if path == '/applicants/top-posts':
            assert params['jobId'] == 'j1' and params['userId']
            return Response({'data': []})
        if path == '/applicants/status' and method == 'POST':
            payload = kwargs['json']
            assert set(payload) == {'userId', 'jobId', 'newStatus'}
            assert payload['jobId'] == 'j1'
            assert kwargs['headers']['Idempotency-Key']
            for a in self.applicants:
                if a['userId'] == payload['userId']:
                    a['status'] = payload['newStatus']
            if self.ambiguous:
                raise RuntimeError('secret-private-data')
            return Response({'data': {'success': True, 'message': 'ok'}})
        raise AssertionError((method, path))


class Tests(unittest.TestCase):
    def setUp(self):
        self.conn = connect(':memory:')
        self.http = HTTP()
        self.client = Client('test-secret', self.http)
        platform = FakePlatform()
        platform.profiles['creator'] = Profile('tiktok', 'creator', 10000)
        platform.posts['creator'] = [Post('https://example.com/post', 'creator', 2000, 100, 0, None)]
        self.adapter = Adapter(lambda: self.client, lambda: {'tiktok': platform})

    def tearDown(self):
        self.conn.close()

    def decision(self, do):
        return self.adapter.action(self.conn, '/extension/sideshift', {'user_id': 'u1', 'job_id': 'j1', 'do': do})

    def test_idempotent_and_snapshot(self):
        self.assertEqual(self.adapter.sync(self.conn)['applicants'], 1)
        self.adapter.sync(self.conn)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM people').fetchone()[0], 1)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM sideshift_applications').fetchone()[0], 1)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM snapshots').fetchone()[0], 1)
        self.assertTrue(self.conn.execute('SELECT score FROM scores').fetchone())
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0], 0)

    def test_no_handles_email_and_pagination(self):
        self.http.applicants = [applicant(tiktok=None, email='creator@example.com'), applicant('u2', tiktok=None)]
        self.assertEqual(self.adapter.sync(self.conn)['applicants'], 2)
        self.adapter.sync(self.conn)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM people').fetchone()[0], 2)
        self.assertEqual(self.conn.execute('SELECT email FROM people WHERE id=1').fetchone()[0], 'creator@example.com')
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM handles').fetchone()[0], 0)

    def test_bad_handle_skips_only_that_handle(self):
        # 2026-10-14: an applicant typed her name ("Don Baari") as her TikTok; the whole sync crashed for a day.
        self.http.applicants = [applicant(tiktok='Don Baari', email='don@example.com'), applicant('u2')]
        result = self.adapter.sync(self.conn)
        self.assertEqual(result['applicants'], 2)
        bad = self.conn.execute("SELECT research_error FROM sideshift_applications WHERE user_id='u1'").fetchone()[0]
        self.assertIn('BadHandle', bad)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) FROM handles WHERE username LIKE '%baari%'").fetchone()[0], 0)
        self.assertEqual(self.conn.execute("SELECT error FROM sideshift_health").fetchone()[0], None)

    def test_identity_conflict_skips_only_that_applicant(self):
        self.http.applicants = [applicant(), applicant('u2', tiktok='@other')]
        self.adapter.sync(self.conn)
        # u2 now claims u1's TikTok and a fresh email: a conflict for u2 alone
        self.http.applicants = [applicant(), applicant('u2', tiktok='@creator', email='new@example.com')]
        self.conn.execute("UPDATE people SET email='old@example.com' WHERE id=(SELECT creator_id FROM sideshift_people WHERE user_id='u1')")
        self.conn.commit()
        result = self.adapter.sync(self.conn)
        self.assertEqual(result['identity_errors'], 1)
        err = self.conn.execute("SELECT research_error FROM sideshift_applications WHERE user_id='u2'").fetchone()[0]
        self.assertIn('Conflict', err)
        self.assertEqual(self.conn.execute("SELECT error FROM sideshift_health").fetchone()[0], None)

    def test_flags(self):
        doc = applicant(country='Canada')
        doc['applicationAnswers'][0]['value'] = '26'
        doc['applicationAnswers'][2]['value'] = False
        doc['applicationAnswers'][3]['value'] = False
        self.assertEqual(flags(doc), ['Not US', 'Age outside 18–25', 'No iPhone + second camera', 'No treadmill/walks'])
        self.assertEqual(flags(applicant()), [])
        self.assertTrue(flags({}))

    def test_accept(self):
        self.adapter.sync(self.conn)
        self.decision('accept')
        self.assertEqual(self.http.applicants[0]['status'], 'Accepted')
        self.assertEqual(self.conn.execute('SELECT stage FROM people').fetchone()[0], 'shortlisted')
        self.assertEqual(self.http.calls[-1][2]['json'], {'userId': 'u1', 'jobId': 'j1', 'newStatus': 'Accepted'})
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0], 0)
        with self.assertRaises(RuntimeError):
            self.decision('accept')

    def test_decline_unscored(self):
        self.http.applicants[0]['tiktok'] = None
        self.adapter.sync(self.conn)
        self.decision('decline')
        self.assertEqual(self.http.calls[-1][2]['json']['newStatus'], 'Declined')
        self.assertEqual(self.conn.execute('SELECT stage FROM people').fetchone()[0], 'declined')

    def test_dnc(self):
        self.adapter.sync(self.conn)
        do_not_contact(self.conn, 1, 'test')
        with self.assertRaisesRegex(RuntimeError, 'DoNotContact'):
            self.decision('accept')
        self.assertFalse(any(m == 'POST' for m, _, _ in self.http.calls))
        self.decision('decline')
        self.assertEqual(self.conn.execute('SELECT do_not_contact FROM people').fetchone()[0], 1)

    def test_stale_decision(self):
        self.adapter.sync(self.conn)
        self.http.applicants[0]['applicationAnswers'][0]['value'] = '30'
        with self.assertRaisesRegex(RuntimeError, 'ApplicationChanged'):
            self.decision('accept')
        self.assertFalse(any(m == 'POST' for m, _, _ in self.http.calls))

    def test_ambiguous_no_resend_and_sync_recovery(self):
        self.adapter.sync(self.conn)
        self.http.ambiguous = True
        with self.assertRaises(RuntimeError):
            self.decision('accept')
        with self.assertRaisesRegex(RuntimeError, 'DecisionUncertain'):
            self.decision('accept')
        self.assertEqual(sum(m == 'POST' for m, _, _ in self.http.calls), 1)
        self.adapter.sync(self.conn)
        self.assertEqual(self.conn.execute('SELECT stage FROM people').fetchone()[0], 'shortlisted')
        self.assertEqual(self.conn.execute('SELECT state FROM sideshift_decisions').fetchone()[0], 'done')

    def test_api_error_cache_and_sanitization(self):
        self.adapter.sync(self.conn)
        self.http.failure = 403
        with self.assertRaisesRegex(RuntimeError, '^SideShift sync: APIError$'):
            self.adapter.sync(self.conn)
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM sideshift_applications').fetchone()[0], 1)
        self.assertNotIn('secret-private-data', self.adapter.render(self.conn))
        with self.assertRaisesRegex(RuntimeError, '^SideShift decision: APIError; sync before retrying$'):
            self.decision('accept')

    def test_rate_limit_no_immediate_retry(self):
        self.http.failure = 429
        with self.assertRaises(RateLimited):
            self.client.request('GET', '/jobs')
        n = len(self.http.calls)
        with self.assertRaises(RateLimited):
            self.client.request('GET', '/jobs')
        self.assertEqual(len(self.http.calls), n)

    def test_missing_key(self):
        adapter = Adapter(lambda: (_ for _ in ()).throw(MissingKey('MissingKey')))
        self.assertEqual(adapter.sync(self.conn), {'disabled': 'MissingKey'})
        self.assertIn('MissingKey', adapter.render(self.conn))

    def test_render_and_route(self):
        self.adapter.sync(self.conn)
        html = self.adapter.render(self.conn)
        self.assertIn('Watch uploaded video', html)
        self.assertIn('Score:', html)
        self.assertIn('name=do value=accept', html)
        self.assertNotIn('Creator <script>', html)
        self.assertFalse(self.adapter.action(self.conn, '/other', {}))

    def test_dashboard_http_extension(self):
        from creatorops.dashboard import make_handler
        with tempfile.TemporaryDirectory(dir=ROOT / 'raw') as directory:
            path = Path(directory) / 'creators.db'
            with connect(path) as conn:
                self.adapter.sync(conn)
            server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(str(path), lambda: {}, lambda: {}, (self.adapter,)))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f'http://127.0.0.1:{server.server_port}'
                page = requests.get(url, timeout=5)
                self.assertEqual(page.status_code, 200)
                self.assertIn('SideShift applicants', page.text)
                response = requests.post(url + '/extension/sideshift', data={'user_id': 'u1', 'job_id': 'j1', 'do': 'accept'}, timeout=5, allow_redirects=False)
                self.assertEqual(response.status_code, 303)
                with connect(path) as conn:
                    self.assertEqual(conn.execute('SELECT stage FROM people').fetchone()[0], 'shortlisted')
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

    def test_composed_contacts_loading(self):
        from run import extensions
        composed = extensions(contacts=True)
        # run.py syncs adapters[0] and adapters[1] by position, so the gate panel must come last.
        self.assertEqual(composed[0].client_factory, Client)
        self.assertEqual(type(composed[1]).__name__, 'InboxAdapter')
        self.assertEqual([type(c).__name__ for c in composed[2:]], ['GatePanel'])

    def test_identity_conflict(self):
        self.adapter.sync(self.conn)
        self.http.applicants.append(applicant('u2', tiktok='second'))
        self.adapter.sync(self.conn)
        self.http.applicants[0]['tiktok'] = 'second'
        # A conflict no longer stops the whole sync; it is recorded on that applicant for review, nobody is merged.
        self.assertEqual(self.adapter.sync(self.conn)['identity_errors'], 1)
        self.assertIn('IdentityConflict', self.conn.execute("SELECT research_error FROM sideshift_applications WHERE user_id='u1'").fetchone()[0])
        self.assertEqual(self.conn.execute('SELECT COUNT(*) FROM people').fetchone()[0], 2)

    def test_advanced_stage_blocks_before_api(self):
        self.adapter.sync(self.conn)
        self.conn.execute('UPDATE people SET stage="signed"')
        self.conn.commit()
        with self.assertRaisesRegex(RuntimeError, 'PipelineConflict'):
            self.decision('accept')
        self.assertFalse(any(m == 'POST' for m, _, _ in self.http.calls))


if __name__ == '__main__':
    unittest.main(verbosity=2)
