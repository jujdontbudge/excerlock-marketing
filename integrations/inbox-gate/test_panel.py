import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'sections/inbox'))
from gate.journal import Journal  # noqa: E402
from gate.model import Action, Decision  # noqa: E402
from panel import GatePanel, rows  # noqa: E402


class Panel(unittest.TestCase):
    def test_shows_waiting_and_hides_done(self):
        with tempfile.TemporaryDirectory() as d:
            j = Journal(Path(d) / 'g.db')
            a = Action(message_type='contract-reminder-1', channel='sideshift', conversation_id='c', source_chat_id='s',
                       person_id='p', creator_key='sideshift:U1', occurrence='C1')
            j.record(a, 'k1', Decision('held', ['she asked something we have not answered: "<b>what?</b>"'], 'Hi <Kamila>'))
            b = Action(message_type='ask-app-email', channel='sideshift', conversation_id='c', source_chat_id='s',
                       person_id='p', creator_key='sideshift:U2')
            j.record(b, 'k2', Decision('held', ['quiet hours']))
            j.record(b, 'k2', Decision('sent', ['ok']))
            j.event('sideshift:U1', 'handle-check', 'm1', {'verdict': 'fail', 'reasons': ['TikTok created 2025-04-06']})
            j.event('sideshift:U2', 'handle-check', 'm2', {'verdict': 'pass', 'reasons': []})
            got = rows(Path(d) / 'g.db')
            self.assertEqual({(r['creator'], r['what']) for r in got},
                             {('sideshift:U1', 'contract-reminder-1: held'), ('sideshift:U1', 'handle-check fail')})
            store = sqlite3.connect(':memory:')
            store.executescript("CREATE TABLE people(id INTEGER, name TEXT); CREATE TABLE sideshift_people(user_id TEXT, creator_id INTEGER);"
                                "INSERT INTO people VALUES (1,'Kamila Rueda'); INSERT INTO sideshift_people VALUES ('U1',1);")
            page = GatePanel(Path(d) / 'g.db').render(store)
            self.assertIn('Kamila Rueda', page)
            self.assertNotIn('<b>what?</b>', page)   # creator text is escaped
            self.assertIn('&lt;Kamila&gt;', page)

    def test_escalations_show_until_answered(self):
        with tempfile.TemporaryDirectory() as d:
            j = Journal(Path(d) / 'g.db')
            j.event('sideshift:U1', 'needs-captain', 'm9', {'from': 'Dakota', 'text': 'cant make a gmail', 'summary': 'NEW QUESTION', 'suggested': 'Use +excerlock'})
            self.assertEqual([r['what'] for r in rows(Path(d) / 'g.db')], ['needs you: Dakota'])
            j.event('sideshift:U1', 'answered', 'm9', {'by': 'captain'})
            self.assertEqual(rows(Path(d) / 'g.db'), [])

    def test_missing_journal_is_fine(self):
        self.assertEqual(rows('/nonexistent/g.db'), [])


if __name__ == '__main__':
    unittest.main()
