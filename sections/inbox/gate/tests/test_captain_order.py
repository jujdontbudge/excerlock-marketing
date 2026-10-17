"""Captain, 2026-10-15: "when I say send, you send". His order skips every judgment hold (her open question, the
review, do-not-contact, quiet hours, pause); only the wrong chat or a double send stops it."""
from dataclasses import replace

from gate.dispatch import text_hash
from gate.model import IN

from .review3.support import Case, Live, Sender, conv, invite, msg


class CaptainOrder(Case):
    def ordered(self, source, reviewer=lambda *a: ('HOLD', 'looks odd', ['her question'])):
        aid = self.j.approve('sideshift:U1', 'example', 'C1', text_hash(self.type.text), 'send it')
        sender = Sender()
        d = self.gate(sender=sender, reviewer=reviewer, source=source,
                      types={'example': replace(self.type, mode='off')}).run(self.action(approval_id=aid))
        return d, sender

    def test_sends_despite_question_review_and_do_not_contact(self):
        self.j.event('sideshift:U1', 'do-not-contact', 'x', {'enabled': True})
        self.paused.touch()
        d, sender = self.ordered(Live(conv(invite(), msg('q', 'Should I send the raw footage here?', direction=IN))))
        self.assertEqual(d.outcome, 'sent', d)
        self.assertEqual(len(sender.calls), 1)

    def test_wrong_chat_still_stops_it(self):
        d, sender = self.ordered(Live(conv(invite(), uid='SOMEONE_ELSE')))
        self.assertEqual(sender.calls, [], d)

    def test_same_text_already_in_chat_still_stops_it(self):
        d, sender = self.ordered(Live(conv(invite(), msg('dup', self.type.text))))
        self.assertEqual(sender.calls, [], d)



class PreflightOrder(Case):
    """The contacts preflight lets his order through his own do-not-contact holds; unreadable routes still stop it."""
    def sender(self, tags, ordered):
        from gate import contacts
        from gate.model import Action
        s = contacts.ContactsMCP.__new__(contacts.ContactsMCP)
        handles = [{'channel': 'sideshift', 'value_normalized': 'U1'}]
        s.call = lambda tool, args: ({'id': 'route1', 'channel': 'sideshift', 'external_id': 'sideshift:chat1',
                                      'participants': [{'value_normalized': 'U1', 'person_id': 'person1'}]}
                                     if tool == 'get_conversation' else
                                     {'person': {'id': 'person1', 'tags': tags, 'handles': handles}})
        s.person_restricted = lambda pid: True
        s.restricted = lambda key: True
        s.captain_ordered = ordered
        a = Action(message_type='example', channel='sideshift', conversation_id='route1', source_chat_id='chat1',
                   person_id='person1', creator_key='sideshift:U1')
        return s, a

    def test_order_passes_do_not_contact(self):
        s, a = self.sender(['do-not-contact'], True)
        s.preflight(a)   # no DefiniteNoSend

    def test_automatic_send_still_stops(self):
        from gate.dispatch import DefiniteNoSend
        for tags in (['do-not-contact'], []):
            s, a = self.sender(tags, False)
            with self.assertRaises(DefiniteNoSend):
                s.preflight(a)
