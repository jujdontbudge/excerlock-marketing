"""Approved message types: one file each in sections/inbox/messages/<id>.md.

Front matter (all required unless marked):
  id: contract-reminder-1
  mode: auto | draft | off          # auto = may send by itself; draft = goes to the captain; off = never
  channel: sideshift
  approved: 2026-10-14 | pending    # 'pending' forces draft until the captain approves the exact text
  fields: [First, first, last]      # the only placeholders the text may use
  once: per_creator | per_occurrence
  quiet_hours: true                 # only 09:00–21:00 America/New_York
  min_gap_minutes: 60               # no send if we (anyone) messaged this chat within this window
  requires: [contract_open, not_accepted]   # state predicates, see checks.STATE
  replaces_unanswered: false        # true only for replies to the creator's own message
The body after the front matter is the exact text. Only {field} placeholders listed in `fields` are filled.
"""
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

MESSAGES = Path(__file__).resolve().parents[1] / 'messages'
PLACEHOLDER = re.compile(r'\{([A-Za-z_]+)\}')
BRACES = re.compile(r'[{}]')
KEYS = {'id', 'mode', 'channel', 'approved', 'fields', 'once', 'quiet_hours', 'min_gap_minutes', 'requires', 'replaces_unanswered'}
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
EMAIL = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$')
NAME = re.compile(r"^[^\W\d_](?:[^\W\d_]|[ .'’-]){0,39}$")
MODES = {'auto', 'draft', 'off'}


class PolicyError(ValueError):
    pass


@dataclass(frozen=True)
class MessageType:
    id: str
    mode: str
    channel: str
    approved: str
    fields: tuple
    once: str
    quiet_hours: bool
    min_gap_minutes: int
    requires: tuple
    replaces_unanswered: bool
    text: str
    source: str = ''   # the file it was read from, re-read right before a send (review U04)

    @property
    def effective_mode(self):
        if self.mode == 'auto' and not real_date(self.approved):
            return 'draft'   # only a real approval date lets a type send by itself (review G15)
        return self.mode


def real_date(value):
    from datetime import date
    try:
        return bool(DATE.match(value or '')) and date.fromisoformat(value) is not None
    except ValueError:
        return False


def _value(raw):
    raw = raw.split('#', 1)[0].strip()          # comments never become part of a value (review G15)
    if raw.startswith('[') and raw.endswith(']'):
        return tuple(x.strip() for x in raw[1:-1].split(',') if x.strip())
    return raw


def _bool(meta, key, default):
    v = meta.get(key, 'true' if default else 'false')
    if v not in ('true', 'false'):
        raise PolicyError(f'{key} must be true or false, not {v!r}')
    return v == 'true'


def parse(path):
    text = Path(path).read_text()
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.S)
    if not m:
        raise PolicyError(f'{path}: missing front matter')
    meta = {}
    for line in m.group(1).splitlines():
        if line.strip() and not line.lstrip().startswith('#'):
            k, sep, v = line.partition(':')
            k = k.strip()
            if not sep or k not in KEYS:
                raise PolicyError(f'{path}: unknown or malformed key {k!r}')
            if k in meta:
                raise PolicyError(f'{path}: duplicate key {k}')
            meta[k] = _value(v)
    body = re.sub(r'<!--.*?-->\n?', '', m.group(2), flags=re.S).strip()
    try:
        approved = str(meta['approved'])
        if approved != 'pending' and not real_date(approved):
            raise PolicyError(f'{path}: approved must be a real date or pending, not {approved!r}')
        gap = meta.get('min_gap_minutes', '60')
        if not str(gap).isdigit():
            raise PolicyError(f'{path}: min_gap_minutes must be a whole number')
        t = MessageType(id=meta['id'], mode=meta['mode'], channel=meta['channel'], approved=approved,
                        fields=tuple(meta.get('fields') or ()), once=meta['once'],
                        quiet_hours=_bool(meta, 'quiet_hours', True), min_gap_minutes=int(gap),
                        requires=tuple(meta.get('requires') or ()),
                        replaces_unanswered=_bool(meta, 'replaces_unanswered', False), text=body, source=str(path))
    except KeyError as missing:
        raise PolicyError(f'{path}: missing {missing}') from None
    if t.id != Path(path).stem:
        raise PolicyError(f'{path}: id {t.id!r} must match the file name')
    if t.mode not in MODES or t.once not in ('per_creator', 'per_occurrence'):
        raise PolicyError(f'{path}: bad mode/once')
    unknown = set(PLACEHOLDER.findall(body)) - set(t.fields)
    if unknown:
        raise PolicyError(f'{path}: text uses placeholders not listed in fields: {sorted(unknown)}')
    if BRACES.search(PLACEHOLDER.sub('', body)):
        raise PolicyError(f'{path}: text has a brace that is not a declared {{field}}')
    if not body:
        raise PolicyError(f'{path}: empty text')
    return t


def load(directory=MESSAGES):
    types = {}
    for p in sorted(Path(directory).glob('*.md')):
        if p.name.startswith('_'):
            continue
        t = parse(p)
        types[t.id] = t
    return types


def valid(name, value):
    """Field-specific checks: names look like names, emails like one email, nothing invisible or control."""
    if not isinstance(value, str):
        return False
    allowed = '\n' if name == 'text' else ''   # the captain's exact words may have line breaks
    if any(unicodedata.category(c).startswith('C') and c not in allowed for c in value):
        return False
    if name in ('First', 'first', 'last'):
        return bool(NAME.match(value))
    if name == 'email':
        return bool(EMAIL.match(value)) and len(value) <= 254
    if name == 'text':
        return 0 < len(value) <= 1000 and '{' not in value and '}' not in value
    return 0 < len(value) <= 80 and not re.search(r'[\n\r{}<>]|https?://', value)


def render(t, fields):
    """Fill exactly the declared placeholders. Missing, empty or invalid values fail closed."""
    out = t.text
    for name in t.fields:
        if f'{{{name}}}' not in out:
            continue
        value = fields.get(name)
        value = value.strip() if isinstance(value, str) else value
        if not value or not valid(name, value):
            raise PolicyError(f'missing or invalid field {name}')
        out = out.replace(f'{{{name}}}', value)
    if BRACES.search(out) and t.id != 'captain-text':
        raise PolicyError('unfilled placeholder')
    return out
