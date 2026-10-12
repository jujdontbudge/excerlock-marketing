#!/usr/bin/env python3
"""Decision log watcher. Archives every Hermes, Claude and Pi session run in this repo as compact
transcripts, has a Pi agent pull the captain's tasks, decisions, corrections and rules out of anything
new, and renders the log. See tools/decision-log/README.md.

Usage: declog.py run | archive | extract | render | status | read <ref> | search <text>
  read hermes-20260924_094051_9aaaf7#120      one message
  read hermes-20260924_094051_9aaaf7#120-140  a range
  read claude-437265ad                        a whole transcript
"""
import fcntl, glob, gzip, hashlib, json, os, re, sqlite3, subprocess, sys, time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOME = os.path.expanduser('~')
LOG = os.path.join(ROOT, 'log')
TR = os.path.join(LOG, 'transcripts')
WORK = os.path.join(LOG, 'work')
STATE = os.path.join(WORK, 'state.json')
EVENTS = os.path.join(LOG, 'events.jsonl')
BRIEF = os.path.join(ROOT, 'tools', 'decision-log', 'brief.md')
# Extraction starts with the 2026-09-24 rebuild session; older archived material is kept but not extracted.
START = datetime(2026, 9, 24, 14, 40, tzinfo=timezone.utc).timestamp()
CHUNK = 200_000  # characters of new transcript per agent run
PI = ['pi', '--provider', 'openai-codex', '--model', 'gpt-6-sol', '--thinking', 'xhigh',
      '--no-session', '--tools', 'read,write', '-p']
TYPES = {'task', 'decision', 'correction', 'agent_run', 'artifact', 'rule', 'open_question'}
SCOPES = {'marketing', 'workflow', 'tooling'}
UPDATABLE = {'status', 'written_in', 'note', 'summary'}

# ---------------------------------------------------------------- redaction

SECRET_RX = re.compile(
    r'sk-[A-Za-z0-9_-]{16,}|AIza[0-9A-Za-z_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|xox[bpa]-[A-Za-z0-9-]{10,}'
    r'|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'
    r'|(?i:(?:api[_-]?key|password|passwd|secret|token|client[_-]?secret)\s*[=:]\s*)\S+')
EMAIL_RX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b')
BLOB_RX = re.compile(r'data:[a-z]+/[a-z0-9.+-]+;base64,[A-Za-z0-9+/=]+|[A-Za-z0-9+/=]{1500,}')
SECRET_FILES = (os.path.join(ROOT, '.env'), f'{HOME}/.config/postiz/tiktok.env',
                f'{HOME}/.config/postiz/tiktok_dev_pw.txt')


def _secret_values():
    vals = set()
    for p in SECRET_FILES:
        try:
            lines = open(p).read().splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, v = line.split('=', 1)
                if not re.search(r'KEY|TOKEN|SECRET|PASS|PW|AUTH|COOKIE', key.upper()):
                    continue  # paths, user ids and user agents are not secrets
            else:
                v = line  # a bare line in a secrets file is treated as a secret
            v = v.strip().strip('"\'')
            if len(v) >= 8:
                vals.add(v)
    return sorted(vals, key=len, reverse=True)


SECRETS = _secret_values()


def clean(s):
    s = s or ''
    for v in SECRETS:
        if v in s:
            s = s.replace(v, '[REDACTED]')
    s = BLOB_RX.sub('[binary]', s)
    s = SECRET_RX.sub('[REDACTED]', s)
    return EMAIL_RX.sub('[email]', s)

# ---------------------------------------------------------------- state


def load_state():
    try:
        st = json.load(open(STATE))
    except (OSError, ValueError):
        st = {}
    for k in ('cursor', 'seen', 'offset', 'n', 'index', 'extracted', 'imgmap'):
        st.setdefault(k, {})
    st.setdefault('ignored', [])
    return st


def save_state(st):
    os.makedirs(WORK, exist_ok=True)
    tmp = STATE + '.tmp'
    json.dump(st, open(tmp, 'w'))
    os.replace(tmp, STATE)


def iso(t):
    return datetime.fromtimestamp(t).astimezone().isoformat(timespec='minutes')

# ---------------------------------------------------------------- archive


def arc_hermes(st, out):
    db = sqlite3.connect(f'file:{HOME}/.hermes/state.db?mode=ro', uri=True)
    sessions = db.execute("select id, title from sessions where cwd=? and coalesce(source,'')!='oneshot' "
                          "order by started_at", (ROOT,)).fetchall()
    for sid, title in sessions:
        key = 'hermes-' + sid
        cur = st['cursor'].get(key, 0)
        seen = set(st['seen'].get(key, []))
        recs = []
        for mid, role, content, calls, tname, ts in db.execute(
                "select id, role, content, tool_calls, tool_name, timestamp from messages "
                "where session_id=? and id>? order by id", (sid, cur)):
            cur = mid
            content = content or ''
            if role == 'user' and content.startswith('[CONTEXT COMPACTION'):
                continue  # compaction handoffs repeat earlier turns
            if len(content) + len(calls or '') >= 40:  # compaction replays copies of earlier messages
                h = hashlib.sha1(f'{role}\0{content}\0{calls or ""}'.encode()).hexdigest()[:16]
                if h in seen:
                    continue
                seen.add(h)
            if role in ('user', 'assistant') and content.strip():
                recs.append((ts, 'user' if role == 'user' else 'hermes', content))
            if role == 'assistant':
                for c in json.loads(calls or '[]'):
                    fn = c.get('function', {})
                    recs.append((ts, 'tool_call', f"{fn.get('name')} {fn.get('arguments', '')}"))
            elif role == 'tool':
                recs.append((ts, 'tool_result', f'{tname}: {content}'))
        st['cursor'][key] = cur
        st['seen'][key] = sorted(seen)
        out[key] = ({'source': 'hermes', 'session': sid, 'title': title}, recs)


def _new_lines(st, path):
    off = st['offset'].get(path, 0)
    if os.path.getsize(path) <= off:
        return []
    with open(path, 'rb') as f:
        f.seek(off)
        data = f.read()
    end = data.rfind(b'\n') + 1
    st['offset'][path] = off + end
    return data[:end].decode('utf-8', 'replace').splitlines()


def _epoch(s):
    try:
        return datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()
    except (AttributeError, ValueError):
        return time.time()


def _result_text(content, image_label):
    if isinstance(content, str):
        return content
    parts = []
    for p in content or []:
        if p.get('type') == 'text':
            parts.append(p.get('text', ''))
        elif p.get('type') == 'image':
            parts.append(image_label)
    return '\n'.join(parts)


def arc_claude(st, out):
    base = f'{HOME}/.claude/projects/' + ROOT.replace('/', '-')
    for path in sorted(glob.glob(base + '/*.jsonl') + glob.glob(base + '/*/subagents/*.jsonl')):
        rel = os.path.relpath(path, base)
        name = os.path.basename(path)[:-6]
        key = 'claude-' + (name[:8] if '/' not in rel else rel.split('/')[0][:8] + '-sub-' + name[6:14])
        lines = _new_lines(st, path)
        if not lines:
            continue
        imgs = st['imgmap'].setdefault(key, {})
        recs = []
        for line in lines:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            msg = e.get('message') or {}
            role = msg.get('role')
            if role not in ('user', 'assistant'):
                continue
            ts = _epoch(e.get('timestamp'))
            parts = msg.get('content')
            if isinstance(parts, str):
                parts = [{'type': 'text', 'text': parts}]
            for p in parts or []:
                t = p.get('type')
                if t == 'text' and p.get('text', '').strip():
                    recs.append((ts, 'user' if role == 'user' else 'agent', p['text']))
                elif t == 'image':
                    recs.append((ts, 'user', '[image]'))
                elif t == 'tool_use':
                    inp = p.get('input') or {}
                    if isinstance(inp, dict) and inp.get('file_path'):
                        imgs[p.get('id')] = inp['file_path']
                    recs.append((ts, 'tool_call', f"{p.get('name')} {json.dumps(inp, ensure_ascii=False)}"))
                elif t == 'tool_result':
                    label = f"[image: {imgs.get(p.get('tool_use_id'), '?')}]"
                    recs.append((ts, 'tool_result', _result_text(p.get('content'), label)))
        if len(imgs) > 500:
            st['imgmap'][key] = dict(list(imgs.items())[-500:])
        prev = out.get(key, ({'source': 'claude', 'file': rel}, []))
        out[key] = (prev[0], prev[1] + recs)


def arc_pi(st, out):
    base = f'{HOME}/.pi/agent/sessions/-' + ROOT.replace('/', '-') + '--'
    for path in sorted(glob.glob(base + '/*.jsonl')):
        key = 'pi-' + os.path.basename(path).rsplit('_', 1)[-1][:8]
        if key in st['ignored']:
            continue
        recs = []
        for line in _new_lines(st, path):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get('type') != 'message':
                continue
            m = e['message']
            role, ts = m.get('role'), _epoch(e.get('timestamp'))
            parts = m.get('content')
            if isinstance(parts, str):
                parts = [{'type': 'text', 'text': parts}]
            if role == 'user':
                text = _result_text(parts, '[image]')
                if text.startswith('# Brief: decision log'):  # the log builder itself
                    st['ignored'].append(key)
                    recs = None
                    break
                recs.append((ts, 'user', text))
            elif role == 'assistant':
                for p in parts or []:
                    if p.get('type') == 'text' and p.get('text', '').strip():
                        recs.append((ts, 'agent', p['text']))
                    elif p.get('type') == 'toolCall':
                        recs.append((ts, 'tool_call', f"{p.get('name')} {json.dumps(p.get('arguments'), ensure_ascii=False)}"))
            elif role == 'toolResult':
                recs.append((ts, 'tool_result', f"{m.get('toolName')}: {_result_text(parts, '[image]')}"))
        if recs:
            out[key] = ({'source': 'pi', 'file': os.path.basename(path)}, recs)


def archive(st):
    out = {}
    arc_hermes(st, out)
    arc_claude(st, out)
    arc_pi(st, out)
    os.makedirs(TR, exist_ok=True)
    added = 0
    for key, (meta, recs) in out.items():
        if not recs:
            continue
        n = st['n'].get(key, 0)
        with gzip.open(os.path.join(TR, key + '.jsonl.gz'), 'at', encoding='utf-8') as f:
            if n == 0:
                f.write(json.dumps({'header': meta}) + '\n')
            for ts, role, text in recs:
                n += 1
                f.write(json.dumps({'n': n, 't': round(ts, 1), 'r': role, 'x': clean(text)}, ensure_ascii=False) + '\n')
        added += len(recs)
        st['n'][key] = n
        idx = st['index'].setdefault(key, dict(meta, first=recs[0][0]))
        idx.update(last=recs[-1][0], count=n)
        if 'brief' not in idx:
            first = next((x for _, r, x in recs if r == 'user'), '')
            idx['brief'] = clean(first)[:200]
    index = {k: dict(v, first=iso(v['first']), last=iso(v['last'])) for k, v in st['index'].items()}
    json.dump(index, open(os.path.join(TR, 'index.json'), 'w'), indent=1, ensure_ascii=False)
    return added

# ---------------------------------------------------------------- extract


def records(key, after=0):
    path = os.path.join(TR, key + '.jsonl.gz')
    if not os.path.exists(path):
        return
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            if r.get('n', 0) > after:
                yield r


def read_events():
    if not os.path.exists(EVENTS):
        return []
    return [json.loads(l) for l in open(EVENTS) if l.strip()]


def fmt(key, r):
    x = r['x']
    lim = {'tool_call': 300, 'tool_result': 200}.get(r['r'])
    if lim and len(x) > lim:
        x = x[:lim] + f' …[+{len(x) - lim} chars]'
    return f"[{key}#{r['n']} {iso(r['t'])} {r['r']}] {x}"


def context_file(events):
    by = {e['id']: e for e in events}
    lines = ['# Existing log (for linking)', '', f'{len(events)} events so far. Full file: log/events.jsonl.', '']
    lines.append('## Rules (all statuses)')
    lines += [f"- {e['id']} [{e.get('scope')}, {e.get('status')}] {e['summary']}" for e in events if e['type'] == 'rule']
    lines.append('\n## Open questions')
    lines += [f"- {e['id']} [{e.get('status')}] {e['summary']}" for e in events if e['type'] == 'open_question']
    lines.append('\n## Last 60 events')
    for e in events[-60:]:
        lines.append(f"- {e['id']} {e.get('time', '')} {e['type']}/{e.get('scope')} phase={e.get('phase')!r}: {e['summary']}"
                     + (f" (links {', '.join(e.get('links') or [])})" if e.get('links') else ''))
    return '\n'.join(lines) + '\n', by


def merge(out_path, events):
    ids = {e['id'] for e in events}
    new, updates = [], []
    for line in open(out_path):
        line = line.strip()
        if not line:
            continue
        e = json.loads(line)
        e = {k: clean(v) if isinstance(v, str) else v for k, v in e.items()}
        if 'update' in e:
            if e['update'] not in ids | {x['id'] for x in new}:
                raise ValueError(f"update for unknown id {e['update']}")
            updates.append(e)
            continue
        missing = {'id', 'type', 'scope', 'summary', 'time'} - set(e)
        if missing or e['type'] not in TYPES or e['scope'] not in SCOPES or e['id'] in ids | {x['id'] for x in new}:
            raise ValueError(f'bad event {e.get("id")}: missing={missing} type={e.get("type")} scope={e.get("scope")}')
        new.append(e)
    allev = events + new
    by = {e['id']: e for e in allev}
    for u in updates:
        tgt = by[u['update']]
        for k in UPDATABLE & set(u):
            tgt[k] = u[k]
        for l in u.get('links_add') or []:
            tgt.setdefault('links', [])
            if l not in tgt['links']:
                tgt['links'].append(l)
    tmp = EVENTS + '.tmp'
    with open(tmp, 'w') as f:
        for e in allev:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')
    os.replace(tmp, EVENTS)
    return len(new), len(updates)


def extract(st, max_chunks=None):
    pending = []
    for key in st['n']:
        for r in records(key, st['extracted'].get(key, 0)):
            if r['t'] >= START:
                pending.append((r['t'], key, r))
            else:
                st['extracted'][key] = r['n']
    pending.sort(key=lambda p: (p[0], p[1], p[2]['n']))
    chunks, cur, size = [], [], 0
    for p in pending:
        line = fmt(p[1], p[2])
        if cur and size + len(line) > CHUNK:
            chunks.append(cur)
            cur, size = [], 0
        cur.append((p, line))
        size += len(line) + 1
    if cur:
        chunks.append(cur)
    done = 0
    for chunk in chunks[:max_chunks]:
        events = read_events()
        ctx, _ = context_file(events)
        os.makedirs(WORK, exist_ok=True)
        delta, ctxp, outp = (os.path.join(WORK, f) for f in ('delta.txt', 'context.md', 'new-events.jsonl'))
        open(delta, 'w').write('\n'.join(l for _, l in chunk) + '\n')
        open(ctxp, 'w').write(ctx)
        open(outp, 'w').close()
        nums = [int(e['id'][1:]) for e in events if re.fullmatch(r'E\d+', e['id'])]
        brief = (open(BRIEF).read().replace('{{DELTA}}', os.path.relpath(delta, ROOT))
                 .replace('{{CONTEXT}}', os.path.relpath(ctxp, ROOT)).replace('{{OUT}}', os.path.relpath(outp, ROOT))
                 .replace('{{NEXT_ID}}', f'E{(max(nums) + 1) if nums else 1:03d}'))
        t0 = time.time()
        res = subprocess.run(PI + [brief], cwd=ROOT, capture_output=True, text=True, timeout=5400)
        with open(os.path.join(WORK, 'runs.log'), 'a') as f:
            f.write(f'\n== {datetime.now().isoformat(timespec="seconds")} chunk {done + 1}/{len(chunks)} '
                    f'{len(chunk)} records, exit {res.returncode}, {time.time() - t0:.0f}s\n{res.stdout[-2000:]}\n{res.stderr[-1000:]}\n')
        if res.returncode != 0:
            raise RuntimeError(f'pi exited {res.returncode}; see log/work/runs.log')
        n_new, n_upd = merge(outp, events)
        for (_, key, r), _ in chunk:
            st['extracted'][key] = max(st['extracted'].get(key, 0), r['n'])
        save_state(st)
        done += 1
        print(f'chunk {done}/{len(chunks)}: {n_new} events, {n_upd} updates')
    return done, len(chunks)

# ---------------------------------------------------------------- render


def when(t):
    try:
        return datetime.fromisoformat(t.replace('Z', '+00:00')).astimezone().strftime('%b %-d %H:%M')
    except (AttributeError, ValueError):
        return t or '?'


def render_one(events, scopes, title, note):
    by = {e['id']: e for e in events}
    shown = [e for e in events if e.get('scope') in scopes]
    L = [f'# {title}', '', note, '']
    L += ['## Recorded rules — verify against canonical files before acting', '']
    for scope in ('marketing', 'workflow', 'tooling'):
        rules = [e for e in shown if e['type'] == 'rule' and e.get('scope') == scope and e.get('status') != 'superseded']
        if not rules:
            continue
        L.append(f'### {scope.capitalize()}')
        for e in rules:
            tag = ' (tentative)' if e.get('status') == 'tentative' else ''
            L.append(f"- **{e['summary']}**{tag} · {e['id']}")
            if e.get('why'):
                L.append(f"  - Why: {e['why']}")
            chain = [l for l in e.get('links') or [] if l in by]
            if chain:
                L.append('  - Came from: ' + ' → '.join(f"{l} ({by[l]['type']}, {when(by[l].get('time'))})" for l in chain))
            L.append(f"  - Written in: {e.get('written_in') or 'not written into the repo yet'}")
        L.append('')
    opens = [e for e in shown if e['type'] == 'open_question' and e.get('status') != 'resolved']
    L += ['## Open questions', '']
    L += [f"- {e['summary']} · {e['id']}, {when(e.get('time'))}" for e in opens] or ['- None.']
    L += ['', '## Timeline', '']
    phase = None
    for e in shown:
        if e['type'] == 'rule':
            continue
        if e.get('phase') != phase:
            phase = e.get('phase')
            L += ['', f'### {phase or "Unsorted"}', '']
        L.append(f"- **{when(e.get('time'))} · {e['type'].replace('_', ' ')} · {e['id']}** {e['summary']}")
        if e.get('captain_quote'):
            L += ['  > ' + q for q in e['captain_quote'].strip().split('\n')]
        if e.get('why'):
            L.append(f"  - Why: {e['why']}")
        extra = []
        if e.get('links'):
            extra.append('links ' + ', '.join(e['links']))
        if e.get('refs'):
            extra.append('source ' + ', '.join(e['refs'][:3]))
        if extra:
            L.append('  - ' + '; '.join(extra))
    return '\n'.join(L).rstrip() + '\n'


def render():
    events = read_events()
    views = os.path.join(LOG, 'views')
    os.makedirs(views, exist_ok=True)
    counts = {s: sum(e.get('scope') == s for e in events) for s in SCOPES}
    how = ('Built automatically every 30 minutes by `tools/decision-log/declog.py` from the Hermes, Claude and Pi '
           'sessions run in this repo. Open any source with `tools/decision-log/declog.py read <source>`.')
    open(os.path.join(views, 'LOG.md'), 'w').write(render_one(
        events, {'marketing', 'workflow'}, 'Marketing decision log',
        how + f" This view shows {counts['marketing']} marketing and {counts['workflow']} workflow events; the "
        f"{counts['tooling']} tooling events are in `log/views/LOG-all.md`. Recorded decisions are evidence, not current policy."))
    open(os.path.join(views, 'LOG-all.md'), 'w').write(render_one(
        events, SCOPES, 'Decision log, every scope', how + ' This view includes tooling events.'))

# ---------------------------------------------------------------- read / search


def read(ref):
    key, _, rng = ref.partition('#')
    lo, _, hi = rng.partition('-')
    lo = int(lo) if lo else 1
    hi = int(hi) if hi else (lo if rng else 10 ** 9)
    for r in records(key, lo - 1):
        if r['n'] > hi:
            break
        print(f"[{key}#{r['n']} {iso(r['t'])} {r['r']}]\n{r['x']}\n")


def search(text):
    rx = re.compile(re.escape(text), re.I)
    for path in sorted(glob.glob(os.path.join(TR, '*.jsonl.gz'))):
        key = os.path.basename(path)[:-9]
        for r in records(key):
            if rx.search(r['x']):
                i = rx.search(r['x']).start()
                print(f"{key}#{r['n']} {iso(r['t'])} {r['r']}: …{r['x'][max(0, i - 80):i + 120]!r}")

# ---------------------------------------------------------------- main


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'run'
    if cmd == 'read':
        return read(sys.argv[2])
    if cmd == 'search':
        return search(' '.join(sys.argv[2:]))
    os.makedirs(WORK, exist_ok=True)
    lock = open(os.path.join(WORK, 'lock'), 'w')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print('another run is in progress')
        return
    st = load_state()
    if cmd == 'status':
        pend = sum(1 for k in st['n'] for r in records(k, st['extracted'].get(k, 0)) if r['t'] >= START)
        print(f"{len(st['n'])} transcripts, {sum(st['n'].values())} messages archived, "
              f"{pend} not yet extracted, {len(read_events())} events")
        return
    if cmd in ('run', 'archive'):
        print(f'archived {archive(st)} new messages')
        save_state(st)
    if cmd in ('run', 'extract'):
        try:
            done, total = extract(st, int(sys.argv[2]) if len(sys.argv) > 2 else None)
            print(f'extracted {done}/{total} chunks')
        finally:
            save_state(st)
            render()
    if cmd == 'render':
        render()


if __name__ == '__main__':
    main()
