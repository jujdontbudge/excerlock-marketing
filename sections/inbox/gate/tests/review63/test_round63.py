"""Offline effect-boundary regressions. Assertions express required behavior.
Run: python3 -m unittest discover -s out/tests -t .
"""
from dataclasses import replace
from datetime import timedelta
from unittest.mock import patch
from types import SimpleNamespace

from gate import checks, policy
from gate.model import Decision, IN
from gate.tests.review4.support import InboxCase, NOW, Live, conv, msg, grant


class PremiumInboxCompletion(InboxCase):
    def repeated_email(self, mode, *, old_send=True, same_batch=False):
        email = 'ada@example.com'
        types = policy.load()
        if mode == 'draft':
            types = {k: replace(t, mode='draft') for k, t in types.items()}
        elif mode == 'mixed':
            automatic = {'contract-reminder-1', 'contract-reminder-2', 'warmup-guide', 'ask-app-email'}
            types = {k: replace(t, mode='auto' if k in automatic else 'draft') for k, t in types.items()}
        t = types['app-access']
        prior = self.action(message_type=t.id, fields={'email': email},
                            contract=self.contract(status='active'))
        # A valid, confirmed old grant and old reply, now revoked. This is NOT an
        # uncertain delivery, a wrong-text receipt, or a missing source message.
        if old_send:
            with patch('gate.journal.datetime') as clock:
                clock.now.return_value = NOW - timedelta(days=1)
                self.grant_receipt(email)
                self.j.record(prior, self.gate(types=types).key(t, prior),
                              Decision('sent', ['confirmed old reply'], policy.render(t, prior.fields)))
            if not same_batch:
                # The real grant helper has already detected and journaled the
                # revocation an hour ago. A repeated submission still disappears.
                commands = []
                def revoked(args, **kw):
                    commands.append(args)
                    return SimpleNamespace(returncode=0, stdout=f'NONE: {email}', stderr='')
                with patch('gate.journal.datetime') as clock:
                    clock.now.return_value = NOW - timedelta(hours=1)
                    ok, line = grant.grant(self.j, prior.creator_key, email, 'offline check', revoked)
                self.assertFalse(ok, line)
                self.assertIn('revoked or ended', line)
                self.assertEqual([a[1] for a in commands], ['check'])
                self.assertIn(f'{email}:revoked', self.j.flags(prior.creator_key, 'grant-error'))
        target = msg('repeated-email', email, direction=IN,
                     at=NOW - timedelta(days=2) if same_batch else NOW - timedelta(minutes=15))
        if same_batch:
            # A receipt can cover another inbox item only if the reply actually
            # answered this exact revision (the normal N29 case).
            self.j.event('sideshift:U1', 'answered', checks.mark(target), {'by': 'app-access'})
        items = [dict(id='new-inbox-item', external_id='sideshift:default:chat1:repeated-email',
                      channel='sideshift', conversation_id='route1', sent_at=target.at, text=email)]
        with patch.object(policy, 'load', return_value=types), \
             patch.object(grant, 'active', return_value=False):
            self.run_inbox(items=items, source=Live(conv(target)))
        self.assertEqual(self.sent, [])
        self.assertEqual(self.external, [], 'A revoked historical grant must never be granted again')

    def test_BY01_auto_must_escalate_new_email_after_old_premium_was_revoked(self):
        self.repeated_email('auto')
        self.assertEqual(self.marked[0]['outcome'], 'escalated', self.output)
        self.assertTrue(self.j.flags('sideshift:U1', 'needs-captain'))

    def test_BY01_drafts_must_surface_new_premium_work_despite_spent_key(self):
        self.repeated_email('draft')
        self.assertEqual(self.marked[0]['outcome'], 'escalated', self.output)
        self.assertTrue(self.j.flags('sideshift:U1', 'needs-captain'))

    def test_BY01_mixed_mode_must_surface_new_premium_work_despite_spent_key(self):
        self.repeated_email('mixed')
        self.assertEqual(self.marked[0]['outcome'], 'escalated', self.output)
        self.assertTrue(self.j.flags('sideshift:U1', 'needs-captain'))

    def test_control_drafts_without_old_send_surface_email(self):
        self.repeated_email('draft', old_send=False)
        self.assertEqual(self.marked[0]['outcome'], 'escalated', self.output)
        self.assertTrue(self.j.flags('sideshift:U1', 'needs-captain'))

    def test_control_already_answered_revision_can_complete_without_resend(self):
        self.repeated_email('draft', same_batch=True)
        self.assertEqual(self.marked[0]['outcome'], 'done', self.output)
