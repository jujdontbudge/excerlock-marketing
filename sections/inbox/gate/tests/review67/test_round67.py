"""Offline regressions: a send receipt must not close newer, unresolved work.

Uses round 66's real gate/reader/journal/ContactsMCP boundary fixture. Only the
external transports and clock are fake. No network, sleeps, or source mutations.
"""
from dataclasses import replace
from datetime import timedelta
from unittest.mock import patch
import json

from gate import policy
from gate.live import SideShiftLive
from gate.tests.review4.support import InboxCase, NOW, contacts
from gate.tests.review66 import test_round66 as previous


class CompletionAfterDelayedSend(InboxCase):
    exercise = previous.DelayedAnswer.exercise

    def delayed(self, **kwargs):
        # Return immediately after the FIRST inbox run. There is no invented
        # second inbox item to rescue work that this run has already closed.
        valid = self.exercise('auto', stop_before_retry=True, **kwargs)
        self.assertFalse(valid, 'CB01 must remain fixed: the reply covers an old generation')
        self.assertEqual(len(self.sent), 1, self.output)
        self.assertEqual(len(self.marked), 1, self.output)
        return self.marked[0]['outcome']

    def test_CC01_auto_must_escalate_current_unresolved_generation(self):
        self.assertEqual(self.delayed(), 'escalated', self.output)

    def test_CC01_cleared_metadata_must_escalate_current_generation(self):
        self.assertEqual(self.delayed(metadata='cleared'), 'escalated', self.output)

    def test_CC01_unresolved_work_must_reach_captain_without_a_second_inbox_item(self):
        self.delayed()
        self.assertTrue(self.j.flags('sideshift:U1', 'needs-captain'),
                        'The stale successful receipt closes the inbox item without surfacing its unresolved generation')

    def test_control_unchanged_delayed_success_completes(self):
        valid = self.exercise('draft', cycle=False, stop_before_retry=True, captain_order=True)
        self.assertTrue(valid)
        self.assertEqual(self.marked[0]['outcome'], 'done', self.output)


class DelayedAutomaticEmailRequest(InboxCase):
    def run_request(self, mode, *, edit=True):
        self.j = self.new_journal(self.root / 'journal.sqlite')
        observer = self.new_journal(self.root / 'journal.sqlite')
        elapsed = [0]
        row = dict(id='status', createdAt=(NOW - timedelta(days=2)).isoformat(),
                   senderUserId='U1', content="I've signed and I'm ready to start")
        company = 'L9suC60QYBRzy8rRY16r1FtjyPT2'

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    return [dict(id='chat1', members=[company, 'U1'])]
                self.assertEqual(path, '/support-channels/chat1/messages')
                return [dict(row)]

        source = SideShiftLive(Client(), company, on_notice=observer.remember_notice)
        item = dict(id='status-item', channel='sideshift', conversation_id='route1',
                    external_id='sideshift:default:chat1:status', sent_at=row['createdAt'], text=row['content'])
        proposal = dict(message_id=item['id'], action='template', message_type='ask-app-email')
        types = policy.load()
        if mode == 'draft':
            types = {k: replace(t, mode='draft') for k, t in types.items()}
        elif mode == 'mixed':
            automatic = {'contract-reminder-1', 'contract-reminder-2', 'warmup-guide', 'ask-app-email'}
            types = {k: replace(t, mode='auto' if k in automatic else 'draft') for k, t in types.items()}
        send = contacts.ContactsMCP.send

        def delayed_response(sender, action, text, send_key, authorized_by,
                             expected_fingerprint=None, recheck=None, observe=None):
            result = send(sender, action, text, send_key, authorized_by,
                          expected_fingerprint=expected_fingerprint, recheck=recheck, observe=observe)
            self.assertEqual(len(self.sent), 1)
            if edit:
                elapsed[0] = 30
                row.update(content='What is the pay rate?', isEdited=True,
                           updatedAt=(NOW + timedelta(seconds=30)).isoformat())
                source.read('chat1', ['U1'])
            elapsed[0] = 60
            return result

        with patch.object(policy, 'load', return_value=types), \
                patch.object(contacts.ContactsMCP, 'send', delayed_response), \
                patch('gate.dispatch.time.monotonic', side_effect=lambda: 1000 + elapsed[0]), \
                patch('gate.journal.datetime') as clock:
            clock.now.side_effect = lambda *a: NOW + timedelta(seconds=elapsed[0])
            self.run_inbox(items=[item], proposals=[proposal], source=source)
        self.assertEqual(self.external, [], 'Email request never grants Premium')
        self.assertEqual(len(self.sent), 0 if mode == 'draft' else 1, self.output)
        seen = [json.loads(e['data'])['text'] for e in observer.events('sideshift:U1') if e['kind'] == 'msg-seen']
        self.assertEqual(len(seen), 2 if edit and mode != 'draft' else 1)
        if edit and mode != 'draft':
            self.assertEqual(seen[-1], 'What is the pay rate?')
            self.assertFalse(self.j.answered('sideshift:U1'))
        return self.marked[0]['outcome']

    def test_CC01_auto_email_request_must_not_close_later_question(self):
        self.assertEqual(self.run_request('auto'), 'escalated', self.output)

    def test_CC01_mixed_auto_email_request_must_not_close_later_question(self):
        self.assertEqual(self.run_request('mixed'), 'escalated', self.output)

    def test_control_drafts_only_escalates_without_sending(self):
        self.assertEqual(self.run_request('draft'), 'escalated', self.output)
        self.assertTrue(self.j.flags('sideshift:U1', 'needs-captain'))

    def test_control_unchanged_automatic_email_request_completes(self):
        self.assertEqual(self.run_request('mixed', edit=False), 'done', self.output)

