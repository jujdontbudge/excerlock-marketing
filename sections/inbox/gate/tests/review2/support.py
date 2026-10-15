"""Offline fixtures. Requests is replaced even when installed; no client can reach a network."""
import importlib
import sys
import tempfile
import types
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from gate import checks, live, policy, review
from gate.dispatch import Gate
from gate.journal import Journal
from gate.model import Action, Conversation, Decision, IN, OUT, Msg


def forbidden(*args, **kwargs):
    raise AssertionError('Network forbidden in review tests')


requests_stub = types.ModuleType('requests')
requests_stub.get = requests_stub.post = forbidden
with patch.dict(sys.modules, {'requests': requests_stub}):
    handles = importlib.import_module('gate.handles')
    contacts_module = importlib.import_module('gate.contacts')
    flow = importlib.import_module('flow')
# patch.dict restores sys.modules on exit. Keep the imported subject modules, whose HTTP
# references still point at the blocked stub; do not install a process-wide requests fake.
sys.modules.update({'gate.handles': handles, 'gate.contacts': contacts_module, 'flow': flow})
seed_module = importlib.import_module('seed_journal')

NOW = datetime(2026, 10, 14, 16, tzinfo=timezone.utc)


def message(id='m1', at='2026-10-14T05:00:00Z', direction=OUT, text='Original invitation', **kw):
    return Msg(id, at, direction, 'creator' if direction == IN else 'company', text,
               kind=kw.pop('kind', live.classify(text)), **kw)


def conversation(*messages, members=('U1',), fp='stable'):
    return Conversation('sideshift', 'chat1', members, tuple(messages), fp, NOW.isoformat())


def raw(**kw):
    data = dict(id='m1', createdAt='2026-10-14T05:00:00Z', content='Original invitation',
                senderUserId='COMPANY', sender='Excerlock')
    data.update(kw)
    return data


def invite(cid='C1', **kw):
    return message(text=f'https://app.sideshift.app/campaign-invite/{cid}?programId=P', **kw)


def request(**kw):
    data = dict(id='h', at='2026-10-14T06:00:00Z', direction=IN,
                text='📨 Requested 2 handles: @new (tiktok), @new (instagram) for this contract.')
    data.update(kw)
    return message(**data)


class StaticLive:
    def __init__(self, conv=None):
        self.conv = conv or conversation(invite())

    def read(self, chat_id, members=None):
        return self.conv


class Pages:
    def __init__(self, rows):
        self.rows = rows

    def pages(self, path, **kwargs):
        return list(self.rows)


class RawClient:
    def __init__(self, rows, members=('U1',)):
        self.rows, self.members = rows, members

    def pages(self, path, **kw):
        if path == '/conversations':
            return [{'id': 'chat1', 'members': ['COMPANY', *self.members]}]
        return list(self.rows)


class Sender:
    def __init__(self, result=None, effect=None):
        self.calls, self.effect = [], effect
        self.result = {'status': 'sent', 'id': 'out1'} if result is None else result

    def send(self, action, text, key, auth):
        self.calls.append((replace(action), text, key, auth))
        if self.effect:
            self.effect()
        return self.result


class RecordingGate:
    def __init__(self):
        self.actions = []

    def run(self, a):
        self.actions.append(a)
        return Decision('held', ['offline recorder'])


class Case(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.journal = self.new_journal()
        self.paused = self.root / 'PAUSED'
        self.clock = NOW
        self.type = policy.MessageType('reminder', 'auto', 'sideshift', '2026-10-14', ('First',),
                                      'per_occurrence', True, 60, ('contract_open', 'not_accepted'),
                                      False, 'Hi {First}, reminder.')

    def new_journal(self):
        j = Journal(self.root / 'gate.db')
        self.addCleanup(j.conn.close)
        return j

    def action(self, **kw):
        data = dict(message_type='reminder', channel='sideshift', conversation_id='route1',
                    source_chat_id='chat1', person_id='person1', creator_key='sideshift:U1',
                    fields={'First': 'Ada'}, occurrence='C1',
                    contract={'id': 'C1', 'status': 'pending', 'contractorId': 'U1',
                              'contractorName': 'Ada Example'})   # adapted 2026-10-15 (BP01): real contracts carry it
        data.update(kw)
        return Action(**data)

    def gate(self, conv=None, source=None, reviewer=None, sender=None, types_=None, journal=None):
        self.sender = sender or Sender()
        return Gate(types_ or {'reminder': self.type}, source or StaticLive(conv),
                    reviewer or (lambda *a: ('SEND', 'offline approval', [])), self.sender,
                    journal or self.journal, now=lambda: self.clock, paused_file=self.paused,
                    applications_reader=lambda uid: [])   # adapted 2026-10-15 (S02)

    def contract(self, **kw):
        c = dict(id='C1', contractorId='U1', contractorName='Ada Example', status='pending')
        c.update(kw)
        return c

    def flow(self, contract=None, conv=None, gate=None, fetchers=None, routes=None):
        source = StaticLive(conv)
        source.client = Pages([{'id': 'chat1', 'members': [flow.COMPANY, 'U1']}])
        self.recorder = gate or RecordingGate()
        return flow.Flow(Pages([contract or self.contract()]), source, self.recorder, self.journal,
                         routes or (lambda chat: ('route1', 'person1')), now=lambda: self.clock,
                         fetchers=fetchers or {'tiktok': lambda h: handles.Profile('tiktok', h, True, NOW, 0, 0),
                                               'instagram': lambda h: handles.Profile('instagram', h, True, None, 0, 0)})

    def policy_file(self, **kw):
        meta = dict(id='example', mode='auto', channel='sideshift', approved='2026-10-14',
                    fields='[First]', once='per_creator', quiet_hours='true', min_gap_minutes='60',
                    requires='[]', replaces_unanswered='false')
        body = kw.pop('body', 'Hi {First}.')
        meta.update(kw)
        p = self.root / 'example.md'
        p.write_text('---\n' + '\n'.join(f'{k}: {v}' for k, v in meta.items()) + '\n---\n' + body)
        return p
