"""Private offline fixtures; real subjects, no source extraction or live services."""
import importlib
import sys
import tempfile
import types
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from gate import checks, policy
from gate.dispatch import Gate
from gate.journal import Journal
from gate.live import classify
from gate.model import Action, Conversation, Decision, Msg, IN, OUT


def forbidden(*a, **kw):
    raise AssertionError('Network forbidden')


http = types.ModuleType('requests')
http.get = http.post = forbidden
with patch.dict(sys.modules, {'requests': http}):
    contacts = importlib.import_module('gate.contacts')
    handles = importlib.import_module('gate.handles')
    flow = importlib.import_module('flow')
sys.modules.update({'gate.contacts': contacts, 'gate.handles': handles, 'flow': flow})
import grant
import propose
import seed_journal
import withdraw

NOW = datetime(2026, 10, 14, 16, tzinfo=timezone.utc)


def msg(id='m1', text='Hello', at=None, direction=OUT, author=None, **kw):
    return Msg(id, (at or NOW - timedelta(hours=10)).isoformat(), direction,
               author or ('creator' if direction == IN else 'company'), text,
               kind=kw.pop('kind', classify(text)), **kw)


def invite(id='invite1', cid='C1', **kw):
    return msg(id, f'https://app.sideshift.app/campaign-invite/{cid}', **kw)


def conv(*messages, uid='U1', chat='chat1', fp='stable'):
    return Conversation('sideshift', chat, (uid,), tuple(messages or (invite(),)), fp, NOW.isoformat())


class Live:
    def __init__(self, conversation=None):
        self.conv = conversation or conv()

    def read(self, *a, **kw):
        return self.conv


class Sender:
    def __init__(self, result=None):
        self.calls = []
        self.result = result or {'status': 'sent', 'id': 'out1'}

    def send(self, *args, **kw):
        self.calls.append((args, kw))
        return self.result


class Case(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.j = self.new_journal()
        self.paused = self.root / 'PAUSED'
        self.type = policy.MessageType('example', 'auto', 'sideshift', '2026-10-14', (),
                                      'per_occurrence', True, 0, (), False, 'Approved message.')

    def new_journal(self, path=':memory:'):
        j = Journal(path)
        self.addCleanup(j.conn.close)
        return j

    def action(self, **kw):
        data = dict(message_type='example', channel='sideshift', conversation_id='route1',
                    source_chat_id='chat1', person_id='person1', creator_key='sideshift:U1',
                    occurrence='C1', fields={}, contract=self.contract())
        data.update(kw)
        return Action(**data)

    def contract(self, **kw):
        return {**dict(id='C1', contractorId='U1', contractorName='Ada Example', status='pending'), **kw}

    def gate(self, sender=None, reviewer=None, source=None, types=None, reader=None):
        return Gate(types or {'example': self.type}, source or Live(),
                    reviewer or (lambda *a: ('SEND', 'offline review', [])), sender or Sender(), self.j,
                    now=lambda: NOW, paused_file=self.paused, contract_reader=reader)

    def no_crash(self, fn):
        try:
            return fn(), None
        except Exception as exc:
            return None, f'{type(exc).__name__}: {exc}'

    def grant_receipt(self, email='ada@example.com'):
        self.j.event('sideshift:U1', 'premium-granted', email, {'email': email, 'result': 'GRANTED: ' + email})
