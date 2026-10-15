"""Offline counterexamples. Assertions state the required behavior, so these fail.

Run: python3 -m unittest discover -s out/tests -t .
Only private journals and fake transports are used; production code is unchanged.
"""
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from gate import checks
from gate.live import SideShiftLive
from gate.model import Decision, IN
from gate.tests.review4.support import (
    Case, InboxCase, NOW, Live, Sender, contacts, conv, invite, msg, policy, propose, withdraw,
)


class CheckedSender(contacts.ContactsMCP):
    """Use the actual preflight/send boundary without HTTP or a running MCP server."""
    def __init__(self, source):
        self.live, self.delivered = source, []

    def call(self, tool, args):
        if tool == 'get_conversation':
            return {'id': args['conversation_id'], 'channel': 'sideshift', 'external_id': 'sideshift:chat1',
                    'participants': [{'value_normalized': 'U1', 'person_id': 'person1'}]}
        if tool == 'get_person':
            return {'id': args['person_id'], 'handles': [], 'tags': []}
        if tool == 'send_message':
            self.delivered.append(args)
            return {'status': 'sent', 'id': 'out1'}
        raise AssertionError(tool)


def raw_photo(**updates):
    # adapted 2026-10-15 (review AN01): real messages always carry updatedAt (292/292 live); without it an
    # unidentified attachment can never be covered by a look, so the gate would hold before the reads tested here
    return {**dict(id='photo', createdAt=(NOW - timedelta(hours=10)).isoformat(),
                   updatedAt=(NOW - timedelta(hours=10)).isoformat(),
                   senderUserId='U1', content='My draft',
                   attachments=[{'name': 'draft.jpg', 'url': 'https://cdn.invalid/old.jpg'}]), **updates}


def photo_source(raw):
    class Client:
        def pages(self, path):
            if path == '/conversations':
                return [{'id': 'chat1', 'members': ['COMPANY', 'U1']}]
            return [raw]
    return SideShiftLive(Client(), 'COMPANY')


class ApplicationAuthority(Case):
    def test_S02_inbox_producer_cannot_omit_application_coverage(self):
        """The real inbox builder/prepare omit the Flow-only applications_required flag."""
        t = policy.load()['contract-reminder-1']
        detail = {'id': 'route1', 'external_id': 'sideshift:chat1',
                  'participants': [{'value_normalized': 'U1', 'person_id': 'person1',
                                    'profile': {'display_name': 'Ada'}}], 'messages': []}
        sender = Sender()
        g = self.gate(types={t.id: t}, sender=sender, reader=lambda cid: self.contract())
        c = SimpleNamespace(call=lambda tool, args: detail)
        outcome, note = propose.handle(
            {'id': 'in1', 'channel': 'sideshift', 'conversation_id': 'route1', 'text': 'Hello'},
            {'action': 'template', 'message_type': t.id}, c, {t.id: t}, [self.contract()],
            self.j, g, False)
        self.assertEqual(sender.calls, [], f'No application evidence, but inbox sends: {outcome}: {note}')

    def test_U01_unknown_request_status_cannot_authorize_withdrawal(self):
        writes = []
        writer = SimpleNamespace(request=lambda *a, **kw: writes.append((a, kw)) or
                                 {'id': 'C1', 'contractorId': 'U1', 'status': 'rejected'})
        # A real request exists; its status is absent, so it is not proven unsigned.
        applications = [{'id': 'req1', 'requestedAt': (NOW - timedelta(hours=39)).isoformat()}]
        withdraw.withdraw('C1', lambda cid: self.contract(),
                          lambda: conv(invite(at=NOW - timedelta(hours=40))),
                          self.j, 'sideshift:U1', NOW, writer, lambda: applications)
        self.assertEqual(writes, [], 'Unknown status was converted to absence of a signing request')


class Triage(InboxCase):
    def test_S11_human_complaint_mentioning_automatic_reply_stays_visible_in_draft_mode(self):
        types = {k: replace(t, mode='draft') for k, t in policy.load().items()}
        with patch.object(policy, 'load', return_value=types):
            self.run_inbox(items=[{'id': 'in1', 'channel': 'email', 'conversation_id': 'route1',
                                   'text': 'Your automatic reply gave me the wrong rate. Payment overdue.'}],
                           proposals=[{'message_id': 'in1', 'action': 'ignore', 'reason': 'auto reply'}])
        self.assertEqual(self.marked[0]['outcome'], 'escalated',
                         'A machine-mail keyword still silently disposes of human mail')

    def test_S10_email_with_new_attachment_is_not_covered_by_old_reply(self):
        t = policy.load()['app-access']
        a = self.action(message_type=t.id, fields={'email': 'ada@example.com'},
                        contract=self.contract(status='active'))
        self.j.record(a, self.gate(types={t.id: t}).key(t, a),
                      Decision('sent', ['old confirmed reply'], policy.render(t, a.fields)))
        self.run_inbox(items=[{'id': 'in1', 'channel': 'sideshift', 'conversation_id': 'route1',
                               'text': 'ada@example.com', 'attachmentCount': 1}],
                       source=Live(conv(msg('new-photo', 'ada@example.com', direction=IN,
                                            attachments=1, attachments_sig='new-unreviewed-image'))))
        self.assertEqual(self.marked[0]['outcome'], 'escalated',
                         'The spent key bypasses completeness; email-only text hides an unseen attachment')


class AttachmentAuthority(Case):
    def test_S15_mixed_attachment_list_cannot_inherit_old_review(self):
        raw = raw_photo(attachments=[{'id': 'stable-id'}, 'https://cdn.invalid/first.jpg'])
        source = photo_source(raw)
        before = source.read('chat1')
        self.j.event('sideshift:U1', 'attachment-reviewed', checks.mark(before.messages[0]), {})
        raw['attachments'][1] = 'https://cdn.invalid/replacement.jpg'
        raw['updatedAt'] = NOW.isoformat()
        sender = Sender()
        self.gate(source=source, sender=sender).run(self.action())
        self.assertEqual(sender.calls, [], 'Filtering non-dicts before all(ids) blesses an unidentified replacement')

    def test_U02_url_only_replacement_in_final_transport_read_must_block(self):
        raw = raw_photo()
        base = photo_source(raw)
        self.j.event('sideshift:U1', 'attachment-reviewed', checks.mark(base.read('chat1').messages[0]), {})
        reads = []
        class Source:
            def read(inner, *args):
                reads.append(1)
                if len(reads) == 3:  # ContactsMCP.send's actual final read, BEFORE its result is compared
                    raw['attachments'][0]['url'] = 'https://cdn.invalid/new-image.jpg'
                return base.read(*args)
        source = Source()
        sender = CheckedSender(source)
        result = self.gate(source=source, sender=sender).run(self.action())
        self.assertEqual(len(reads), 3)
        self.assertTrue(checks.completeness(base.read('chat1'), self.j.flags('sideshift:U1', 'attachment-reviewed')))
        self.assertEqual(sender.delivered, [], f'Final read sees different media but accepts equal fingerprint: {result.outcome}')


class FinalBoundary(Case):
    def test_U03_contract_activation_during_final_transport_read_blocks_reminder(self):
        t = policy.load()['contract-reminder-1']
        current = self.contract(applications=[], applications_required=True)
        reads = []
        clock = [NOW]
        class Source:
            def read(inner, *args):
                reads.append(1)
                if len(reads) == 3:
                    clock[0] += timedelta(minutes=2)  # membership + paginated history can be slow
                    current['status'] = 'active'  # no new chat notice, as in the round-six T02 scenario
                return conv(invite())
        source = Source()
        sender = CheckedSender(source)
        g = self.gate(types={t.id: t}, source=source, sender=sender, reader=lambda cid: dict(current))
        g.now = lambda: clock[0]
        g.applications_reader = lambda uid: []
        result = g.run(self.action(message_type=t.id, fields={'First': 'Ada'}, contract=dict(current)))
        self.assertEqual(len(reads), 3)
        self.assertEqual(sender.delivered, [], f'Contract validation precedes another live transport read: {result.outcome}')

    def test_U04_off_switch_during_review_stops_inflight_auto_send(self):
        path = self.root / 'example.md'
        path.write_text('---\nid: example\nmode: auto\nchannel: sideshift\napproved: 2026-10-14\n'
                        'fields: []\nonce: per_occurrence\nquiet_hours: true\nmin_gap_minutes: 0\n'
                        'requires: []\n---\nApproved message.')
        types = policy.load(self.root)
        def reviewer(*args):
            path.write_text(path.read_text().replace('mode: auto', 'mode: off'))
            return 'SEND', 'previous mode was auto', []
        sender = Sender()
        self.gate(types=types, sender=sender, reviewer=reviewer).run(self.action())
        self.assertEqual(policy.load(self.root)['example'].effective_mode, 'off')
        self.assertEqual(sender.calls, [], 'Documented per-type stop switch is never refreshed during a run')
