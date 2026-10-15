"""Offline effect-boundary regressions for observed edits without a reliable revision clock.
Assertions describe required behavior. Run from the snapshot root:
python3 -m unittest discover -s out/tests -t .
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch
import json

from gate import checks, policy
from gate.live import SideShiftLive
from gate.tests.review4.support import InboxCase, NOW, grant


class ObservedEditCycle(InboxCase):
    def resubmit(self, mode, *, transition=True, metadata='unknown', new_clock=False):
        email = 'ada@example.com'
        row = dict(id='email', createdAt=(NOW - timedelta(days=2)).isoformat(),
                   senderUserId='U1', content=email)
        if metadata == 'unknown':
            row.update(isEdited=True)  # accepted by the real reader as edited_at='unknown'
        company = 'L9suC60QYBRzy8rRY16r1FtjyPT2'

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    return [dict(id='chat1', members=[company, 'U1'])]
                self.assertEqual(path, '/support-channels/chat1/messages')
                return [dict(row)]

        source = SideShiftLive(Client(), company, on_notice=self.j.remember_notice)
        item = dict(id='original-item', channel='sideshift', conversation_id='route1',
                    external_id='sideshift:default:chat1:email', sent_at=row['createdAt'], text=email)
        # Establish a REAL successful gate reply and its answer mark, not a legacy fixture token.
        with patch('gate.journal.datetime') as clock:
            clock.now.return_value = NOW - timedelta(days=1)
            self.run_inbox(items=[item], source=source)
        self.assertEqual(len(self.sent), 1, self.output)
        self.assertEqual(self.marked[0]['outcome'], 'done', self.output)
        original = source.read('chat1', ['U1']).messages[0]
        old_token = checks.answer_mark(original)
        self.assertIn(old_token, self.j.flags('sideshift:U1', 'answered'))

        # The real grant helper subsequently detects revocation; it must never re-grant.
        commands = []
        def revoked(argv, **kwargs):
            commands.append(argv)
            return SimpleNamespace(returncode=0, stdout=f'NONE: {email}', stderr='')
        with patch('gate.journal.datetime') as clock:
            clock.now.return_value = NOW - timedelta(hours=1)
            ok, line = grant.grant(self.j, 'sideshift:U1', email, 'offline check', revoked)
        self.assertFalse(ok, line)
        self.assertIn('revoked or ended', line)
        self.assertEqual([a[1] for a in commands], ['check'])

        if transition:
            row.update(content='replacement@example.com', isEdited=True)
            if metadata == 'cleared':
                row['updatedAt'] = (NOW - timedelta(minutes=30)).isoformat()
            with patch('gate.journal.datetime') as clock:
                clock.now.return_value = NOW - timedelta(minutes=30)
                source.read('chat1', ['U1'])
            row['content'] = email
            if metadata == 'cleared':
                row.pop('updatedAt')
                row['isEdited'] = False
        if new_clock:
            row.update(isEdited=True, updatedAt=(NOW - timedelta(minutes=15)).isoformat())
        with patch('gate.journal.datetime') as clock:
            clock.now.return_value = NOW - timedelta(minutes=15)
            current = source.read('chat1', ['U1']).messages[0]
        if transition:
            observed = [json.loads(e['data'])['text'] for e in self.j.events('sideshift:U1')
                        if e['kind'] == 'msg-seen']
            self.assertIn('replacement@example.com', observed)
        if transition and not new_clock:
            self.assertEqual(old_token, checks.answer_mark(current), 'This is the alias being exercised')

        types = policy.load()
        if mode == 'draft':
            types = {k: replace(t, mode='draft') for k, t in types.items()}
        elif mode == 'mixed':
            automatic = {'contract-reminder-1', 'contract-reminder-2', 'warmup-guide', 'ask-app-email'}
            types = {k: replace(t, mode='auto' if k in automatic else 'draft') for k, t in types.items()}
        item['id'] = 'resubmitted-item'
        with patch.object(policy, 'load', return_value=types), patch.object(grant, 'active', return_value=False):
            self.run_inbox(items=[item], source=source)
        self.assertEqual(self.sent, [])
        self.assertEqual(self.external, [], 'No second grant or entitlement check took place')
        return self.marked[0]['outcome']

    def test_CA01_auto_must_escalate_observed_cycle_with_unknown_edit_clock(self):
        self.assertEqual(self.resubmit('auto'), 'escalated', self.output)
        self.assertTrue(self.j.flags('sideshift:U1', 'needs-captain'))

    def test_CA01_drafts_must_escalate_observed_cycle_with_unknown_edit_clock(self):
        self.assertEqual(self.resubmit('draft'), 'escalated', self.output)
        self.assertTrue(self.j.flags('sideshift:U1', 'needs-captain'))

    def test_CA01_mixed_must_escalate_observed_cycle_with_unknown_edit_clock(self):
        self.assertEqual(self.resubmit('mixed'), 'escalated', self.output)
        self.assertTrue(self.j.flags('sideshift:U1', 'needs-captain'))

    def test_CA01_cleared_edit_metadata_cannot_restore_legacy_answer_authority(self):
        self.assertEqual(self.resubmit('draft', metadata='cleared'), 'escalated', self.output)

    def test_control_unchanged_answered_unknown_clock_can_complete(self):
        self.assertEqual(self.resubmit('draft', transition=False), 'done', self.output)

    def test_control_restored_content_with_fresh_clock_escalates(self):
        self.assertEqual(self.resubmit('draft', new_clock=True), 'escalated', self.output)
