"""Offline regressions at real gate/SideShiftLive/ContactsMCP boundaries.

Only external transports, the reviewer verdict and clocks are fake. Production
sources are unchanged; all writes are to private temporary files/databases.
"""
import json
from datetime import timedelta
from unittest.mock import patch

from gate import checks, policy
from gate.dispatch import Gate
from gate.live import SideShiftLive
from gate.tests.review4.support import InboxCase, NOW, contacts, propose


class RestoredHistoricalRevision(InboxCase):
    def exercise(self, *, request_email=False, old_history=True, restore=True):
        self.j = self.new_journal(self.root / 'history.sqlite')
        observer = self.new_journal(self.root / 'history.sqlite')
        key = 'sideshift:U1'
        elapsed = [0]
        old, reviewed = 'replacement@example.com', 'ada@example.com'
        kind = 'app-access'
        if request_email:
            old, reviewed = 'What is the pay rate?', "I've signed and I'm ready to start"
            kind = 'ask-app-email'
        row = dict(id='email', createdAt=(NOW - timedelta(days=2)).isoformat(),
                   senderUserId='U1', content=old, isEdited=True)
        company = 'L9suC60QYBRzy8rRY16r1FtjyPT2'

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    return [dict(id='chat1', members=[company, 'U1'])]
                self.assertEqual(path, '/support-channels/chat1/messages')
                return [dict(row)]

        source = SideShiftLive(Client(), company, on_notice=observer.remember_notice)
        if old_history:
            source.read('chat1', ['U1'])
        row['content'] = reviewed
        item = dict(id='email-item', channel='sideshift', conversation_id='route1',
                    external_id='sideshift:default:chat1:email', sent_at=row['createdAt'], text=reviewed)
        types = policy.load()
        real_send = contacts.ContactsMCP.send
        switch = self.root / 'INBOX_AUTO'
        switch.touch()
        proposal = dict(message_id=item['id'], action='template', message_type=kind,
                        fields={} if request_email else {'email': reviewed})

        def delayed(sender, action, text, send_key, authorized_by,
                    expected_fingerprint=None, recheck=None, observe=None):
            result = real_send(sender, action, text, send_key, authorized_by,
                               expected_fingerprint=expected_fingerprint, recheck=recheck, observe=observe)
            self.assertEqual(len(self.sent), 1, self.output if hasattr(self, 'output') else '')
            if restore:
                elapsed[0] = 30
                row['content'] = old
                source.read('chat1', ['U1'])
            elapsed[0] = 60
            return result

        with patch.object(propose, 'INBOX_AUTO', switch), \
                patch.object(contacts.ContactsMCP, 'send', delayed), \
                patch('gate.dispatch.time.monotonic', side_effect=lambda: 1000 + elapsed[0]), \
                patch('gate.journal.datetime') as clock:
            clock.now.side_effect = lambda *a: NOW + timedelta(seconds=elapsed[0])
            self.run_inbox(items=[item], proposals=[proposal], source=source)
        self.assertEqual(len(self.sent), 1, self.output)
        self.assertEqual(self.sent[0]['text'], policy.render(types[kind], {} if request_email else {'email': reviewed}))
        self.assertEqual(len(self.marked), 1, self.output)
        seen = [json.loads(e['data'])['text'] for e in self.j.events(key) if e['kind'] == 'msg-seen']
        self.assertEqual(seen, ([old] if old_history else []) + [reviewed] + ([old] if restore else []))
        self.current = source.read('chat1', ['U1']).messages[0]
        return self.marked[0]['outcome']

    def test_CD01_auto_must_escalate_restored_historical_request(self):
        self.assertEqual(self.exercise(), 'escalated', self.output)

    def test_CD01_email_request_must_escalate_restored_pay_question(self):
        self.assertEqual(self.exercise(request_email=True), 'escalated', self.output)

    def test_control_CB01_answer_authority_still_rejects_restored_request(self):
        self.exercise()
        self.assertNotIn(checks.answer_mark(self.current), self.j.answered('sideshift:U1'),
                         'The delayed reply for ada@example.com answers the revived replacement@example.com request')

    def test_CD01_restored_request_must_reach_captain(self):
        self.exercise()
        self.assertTrue(self.j.flags('sideshift:U1', 'needs-captain'), self.output)

    def test_control_novel_later_revision_escalates(self):
        self.assertEqual(self.exercise(old_history=False), 'escalated', self.output)

    def test_control_unchanged_source_with_old_history_completes(self):
        self.assertEqual(self.exercise(restore=False), 'done', self.output)


class InboxSwitchDuringReview(InboxCase):
    def exercise(self, *, disable=False, default_draft=False):
        switch = self.root / 'INBOX_AUTO'
        if not default_draft:
            switch.touch()
        elapsed, reviewed = [0], []
        row = dict(id='ready', createdAt=(NOW - timedelta(days=2)).isoformat(),
                   senderUserId='U1', content="I've signed and I'm ready to start")
        company = 'L9suC60QYBRzy8rRY16r1FtjyPT2'

        class Client:
            def pages(inner, path, **kwargs):
                if path == '/conversations':
                    return [dict(id='chat1', members=[company, 'U1'])]
                self.assertEqual(path, '/support-channels/chat1/messages')
                return [dict(row)]

        source = SideShiftLive(Client(), company, on_notice=self.j.remember_notice)
        item = dict(id='ready-item', channel='sideshift', conversation_id='route1',
                    external_id='sideshift:default:chat1:ready', text=row['content'])
        proposal = dict(message_id=item['id'], action='template', message_type='ask-app-email')

        def review(gate, conv, text, kind):
            reviewed.append(kind)
            if disable:
                switch.unlink()
            elapsed[0] = 60
            return 'SEND', 'unchanged chat, email request appropriate', []

        real_guarded = Gate._guarded

        def guarded(gate, *args):
            gate.reviewer = lambda *a: review(gate, *a)
            return real_guarded(gate, *args)

        with patch.object(propose, 'INBOX_AUTO', switch), patch.object(Gate, '_guarded', guarded), \
                patch('gate.dispatch.time.monotonic', side_effect=lambda: 1000 + elapsed[0]):
            self.run_inbox(items=[item], proposals=[proposal], source=source)
        self.assertEqual(self.external, [])
        self.assertEqual(len(reviewed), 0 if default_draft else 1)
        if disable:
            self.assertFalse(switch.exists())
        return len(self.sent)

    def test_CD02_removing_inbox_auto_during_review_must_stop_send(self):
        self.assertEqual(self.exercise(disable=True), 0,
                         'INBOX_AUTO was removed 60 seconds before the automatic inbox send')

    def test_control_switch_kept_on_sends(self):
        self.assertEqual(self.exercise(), 1, self.output)

    def test_control_switch_absent_from_start_drafts(self):
        self.assertEqual(self.exercise(default_draft=True), 0, self.output)
