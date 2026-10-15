"""Offline effect-boundary regressions. Assertions state required behavior.
Run: python3 -m unittest discover -s out/tests -t .
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from gate import checks, policy
from gate.live import SideShiftLive, revision_key
from gate.model import Decision
from gate.tests.review4.support import InboxCase, NOW, grant


class EditedPremiumSubmission(InboxCase):
    def run_resubmission(self, mode, *, edited=True, remark=False, new_id=False):
        email = 'ada@example.com'
        types = policy.load()
        if mode == 'draft':
            types = {k: replace(t, mode='draft') for k, t in types.items()}
        elif mode == 'mixed':
            automatic = {'contract-reminder-1', 'contract-reminder-2', 'warmup-guide', 'ask-app-email'}
            types = {k: replace(t, mode='auto' if k in automatic else 'draft') for k, t in types.items()}
        t = types['app-access']
        prior = self.action(message_type=t.id, fields={'email': email}, contract=self.contract(status='active'))
        row = dict(id='email', createdAt=(NOW - timedelta(days=2)).isoformat(),
                   senderUserId='U1', content=email)
        company = 'L9suC60QYBRzy8rRY16r1FtjyPT2'

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    return [dict(id='chat1', members=[company, 'U1'])]
                self.assertEqual(path, '/support-channels/chat1/messages')
                return [dict(row)]

        # Real reader and journal: yesterday's email was actually seen and answered.
        source = SideShiftLive(Client(), company, on_notice=self.j.remember_notice)
        original = source.read('chat1', ['U1']).messages[0]
        with patch('gate.journal.datetime') as clock:
            clock.now.return_value = NOW - timedelta(days=1)
            self.grant_receipt(email)
            self.j.record(prior, self.gate(types=types).key(t, prior),
                          Decision('sent', ['confirmed old reply'], policy.render(t, prior.fields)))
            self.j.event(prior.creator_key, 'answered', checks.mark(original), {'by': 'app-access'})

        # The real helper detects a later revocation. No re-grant is authorized.
        commands = []
        def revoked(argv, **kwargs):
            commands.append(argv)
            return SimpleNamespace(returncode=0, stdout=f'NONE: {email}', stderr='')
        with patch('gate.journal.datetime') as clock:
            clock.now.return_value = NOW - timedelta(hours=1)
            ok, line = grant.grant(self.j, prior.creator_key, email, 'offline check', revoked)
        self.assertFalse(ok, line)
        self.assertIn('revoked or ended', line)
        self.assertEqual([a[1] for a in commands], ['check'])

        if edited:
            # She changes the old email to a replacement, then restores her old
            # account after discovering that it no longer has Premium. Both
            # edits are visible through the real reader, well outside 10 seconds.
            row.update(content='replacement@example.com', isEdited=True,
                       updatedAt=(NOW - timedelta(minutes=30)).isoformat())
            source.read('chat1', ['U1'])
            row.update(content=email, updatedAt=(NOW - timedelta(minutes=15)).isoformat())
        if new_id:
            row['id'] = 'new-email'
            row['createdAt'] = (NOW - timedelta(minutes=15)).isoformat()
        current = source.read('chat1', ['U1']).messages[0]
        if edited or new_id:
            self.assertNotEqual(revision_key(original), revision_key(current))
        if remark:
            # adapted 2026-10-15 (BZ01 fix): record.py writes the edit-bound answer token
            self.j.event(prior.creator_key, 'answered', checks.answer_mark(current), {'by': 'captain'})

        item = dict(id='resubmitted-item', channel='sideshift', conversation_id='route1',
                    external_id=f'sideshift:default:chat1:{row["id"]}', sent_at=current.at, text=email)
        with patch.object(policy, 'load', return_value=types), patch.object(grant, 'active', return_value=False):
            self.run_inbox(items=[item], source=source)
        self.assertEqual(self.sent, [])
        self.assertEqual(self.external, [], 'A revoked account must not be re-granted')
        return self.marked[0]['outcome']

    def test_BZ01_auto_must_escalate_later_edited_revision(self):
        self.assertEqual(self.run_resubmission('auto'), 'escalated', self.output)
        self.assertTrue(self.j.flags('sideshift:U1', 'needs-captain'))

    def test_BZ01_drafts_must_escalate_later_edited_revision(self):
        self.assertEqual(self.run_resubmission('draft'), 'escalated', self.output)
        self.assertTrue(self.j.flags('sideshift:U1', 'needs-captain'))

    def test_BZ01_mixed_mode_must_escalate_later_edited_revision(self):
        self.assertEqual(self.run_resubmission('mixed'), 'escalated', self.output)
        self.assertTrue(self.j.flags('sideshift:U1', 'needs-captain'))

    def test_control_unchanged_answered_revision_can_complete(self):
        self.assertEqual(self.run_resubmission('draft', edited=False), 'done', self.output)

    def test_control_captain_can_settle_current_edited_revision(self):
        self.assertEqual(self.run_resubmission('draft', remark=True), 'done', self.output)

    def test_control_new_message_id_escalates(self):
        self.assertEqual(self.run_resubmission('draft', edited=False, new_id=True), 'escalated', self.output)
