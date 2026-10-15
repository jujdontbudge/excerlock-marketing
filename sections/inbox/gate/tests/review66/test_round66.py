"""Offline effect-boundary regressions; assertions describe the required outcome.

The send succeeds before the edits. Its response takes 60s (< ContactsMCP's 90s
timeout). A second SQLite connection observes the edits during that wait. No sleep,
network, actual access command, or production file mutation is used.
"""
from dataclasses import replace
from datetime import timedelta
from unittest.mock import patch
import json

from gate import checks, policy
from gate.dispatch import Gate, text_hash
from gate.live import SideShiftLive
from gate.tests.review4.support import InboxCase, NOW, contacts, grant


class DelayedAnswer(InboxCase):
    def exercise(self, mode='draft', *, cycle=True, metadata='unknown',
                 captain_resolution=False, stop_before_retry=False, captain_order=False):
        self.j = self.new_journal(self.root / 'journal.sqlite')
        observer = self.new_journal(self.root / 'journal.sqlite')
        key, email = 'sideshift:U1', 'ada@example.com'
        elapsed = [0]
        row = dict(id='email', createdAt=(NOW - timedelta(days=2)).isoformat(),
                   senderUserId='U1', content=email)
        if metadata == 'unknown':
            row['isEdited'] = True
        company = 'L9suC60QYBRzy8rRY16r1FtjyPT2'

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    return [dict(id='chat1', members=[company, 'U1'])]
                self.assertEqual(path, '/support-channels/chat1/messages')
                return [dict(row)]

        source = SideShiftLive(Client(), company, on_notice=observer.remember_notice)
        item = dict(id='original-item', channel='sideshift', conversation_id='route1',
                    external_id='sideshift:default:chat1:email',
                    sent_at=row['createdAt'], text=email)
        types = policy.load()
        if mode == 'draft':
            types = {k: replace(t, mode='draft') for k, t in types.items()}
        elif mode == 'mixed':
            automatic = {'contract-reminder-1', 'contract-reminder-2', 'warmup-guide', 'ask-app-email'}
            types = {k: replace(t, mode='auto' if k in automatic else 'draft') for k, t in types.items()}
        run = Gate.run

        def ordered_run(gate, action):
            # Draft/mixed modes still support the captain's one-use exact-text send.
            text = policy.render(gate.types[action.message_type], action.fields)
            action.captain_order = 'send these exact Premium instructions'
            action.approval_id = self.j.approve(key, action.message_type, action.occurrence,
                                              text_hash(text), action.captain_order)
            return run(gate, action)
        send = contacts.ContactsMCP.send

        def delayed_response(sender, action, text, send_key, authorized_by,
                             expected_fingerprint=None, recheck=None, observe=None):
            # Execute the REAL ContactsMCP checks and send boundary first.
            result = send(sender, action, text, send_key, authorized_by,
                          expected_fingerprint=expected_fingerprint, recheck=recheck, observe=observe)
            self.assertEqual(len(self.sent), 1)
            self.assertFalse(self.j.answered(key))  # no answer fact written yet
            elapsed[0] = 15
            ok, line = grant.grant(observer, key, email, 'revocation check')
            self.assertFalse(ok, line)
            self.assertIn('revoked or ended', line)
            if cycle:
                elapsed[0] = 30
                row.update(content='replacement@example.com', isEdited=True)
                if metadata == 'cleared':
                    row['updatedAt'] = (NOW + timedelta(seconds=30)).isoformat()
                source.read('chat1', ['U1'])
                elapsed[0] = 45
                row['content'] = email
                if metadata == 'cleared':
                    row.pop('updatedAt')
                    row['isEdited'] = False
                source.read('chat1', ['U1'])
            elapsed[0] = 60
            return result

        with patch('gate.dispatch.time.monotonic', side_effect=lambda: 1000 + elapsed[0]), \
                patch('gate.journal.datetime') as clock:
            clock.now.side_effect = lambda *a: NOW + timedelta(seconds=elapsed[0])
            with patch.object(contacts.ContactsMCP, 'send', delayed_response):
                if captain_order:
                    with patch.object(policy, 'load', return_value=types), patch.object(Gate, 'run', ordered_run):
                        self.run_inbox(items=[item], source=source)
                else:
                    self.run_inbox(items=[item], source=source)
            self.assertEqual(len(self.sent), 1, self.output)
            events = self.j.events(key)
            observed = [json.loads(e['data'])['text'] for e in events if e['kind'] == 'msg-seen']
            self.assertEqual(observed, [email, 'replacement@example.com', email] if cycle else [email])
            current = source.read('chat1', ['U1']).messages[0]
            token = checks.answer_mark(current)
            # Verify that this is a late writer, distinct from CA01's old-token reuse.
            answers = [e for e in events if e['kind'] == 'answered']
            self.assertLessEqual(len(answers), 1)
            for answer in answers:
                self.assertEqual(answer['at'], (NOW + timedelta(seconds=60)).isoformat())
                self.assertGreater(answer['id'], max(e['id'] for e in events if e['kind'] == 'msg-seen'))
            if stop_before_retry:
                return token in self.j.answered(key)
            if captain_resolution:
                self.j.answer(key, token, {'by': 'captain', 'why': 'handled current request manually'})

            elapsed[0] = 1800  # restored source state is stable for >29 minutes
            item['id'] = 'later-item'
            with patch.object(policy, 'load', return_value=types), patch.object(grant, 'active', return_value=False):
                self.run_inbox(items=[item], source=source)
            self.assertEqual(self.sent, [])
            self.assertEqual(self.external, [])
            return self.marked[0]['outcome']

    def test_CB01_post_send_mark_must_not_answer_a_later_observed_generation(self):
        self.assertFalse(self.exercise(stop_before_retry=True),
                         'The late send result writes a fresh answer for the pre-send generation')

    def test_CB01_auto_must_keep_restored_premium_request_open(self):
        self.assertEqual(self.exercise('auto'), 'escalated', self.output)

    def test_CB01_draft_must_keep_restored_premium_request_open(self):
        self.assertEqual(self.exercise('draft', captain_order=True), 'escalated', self.output)

    def test_CB01_mixed_must_keep_restored_premium_request_open(self):
        self.assertEqual(self.exercise('mixed', captain_order=True), 'escalated', self.output)

    def test_CB01_cleared_edit_metadata_must_keep_restored_request_open(self):
        self.assertEqual(self.exercise('draft', metadata='cleared', captain_order=True), 'escalated', self.output)

    def test_control_delayed_response_without_edits_preserves_completion(self):
        self.assertEqual(self.exercise(cycle=False), 'done', self.output)

    def test_control_fresh_captain_resolution_can_settle_current_generation(self):
        self.assertEqual(self.exercise(captain_resolution=True), 'done', self.output)
