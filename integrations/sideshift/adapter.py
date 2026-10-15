"""Adapter-owned identities/applications and owner-only decisions in the existing CRM."""
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from html import escape
from urllib.parse import quote, urlparse

from creatorops import intake, pipeline, snapshot, vetting
from creatorops.db import event, now
from creatorops.platforms import default_platforms, parse_link
from client import Client, MissingKey, ProtocolError

SCHEMA = '''
CREATE TABLE IF NOT EXISTS sideshift_people (
 user_id TEXT PRIMARY KEY, creator_id INTEGER NOT NULL REFERENCES people(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS sideshift_applications (
 user_id TEXT NOT NULL REFERENCES sideshift_people(user_id) ON DELETE CASCADE,
 job_id TEXT NOT NULL, document TEXT NOT NULL, job TEXT NOT NULL, top_posts TEXT NOT NULL,
 status TEXT NOT NULL, updated_at TEXT NOT NULL, research_error TEXT,
 PRIMARY KEY(user_id, job_id)
);
CREATE TABLE IF NOT EXISTS sideshift_decisions (
 user_id TEXT NOT NULL, job_id TEXT NOT NULL, status TEXT NOT NULL, request_id TEXT NOT NULL,
 state TEXT NOT NULL, error TEXT, PRIMARY KEY(user_id, job_id),
 FOREIGN KEY(user_id,job_id) REFERENCES sideshift_applications(user_id,job_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS sideshift_health (
 id INTEGER PRIMARY KEY CHECK(id=1), last_attempt TEXT, last_sync TEXT, error TEXT
);
INSERT OR IGNORE INTO sideshift_health(id) VALUES(1);
'''


def setup(conn):
    conn.executescript(SCHEMA)


US_STATES = set("al ak az ar ca co ct de fl ga hi id il in ia ks ky la me md ma mi mn ms mo mt ne nv nh nj nm ny nc nd oh ok or pa ri sc sd tn tx ut vt va wa wv wi wy dc".split())
US_STATES.update("alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|florida|georgia|hawaii|idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|maine|maryland|massachusetts|michigan|minnesota|mississippi|missouri|montana|nebraska|nevada|new hampshire|new jersey|new mexico|new york|north carolina|north dakota|ohio|oklahoma|oregon|pennsylvania|rhode island|south carolina|south dakota|tennessee|texas|utah|vermont|virginia|washington|west virginia|wisconsin|wyoming|district of columbia".split('|'))


def flags(document):
    """Conservative hints: unanswered/ambiguous requirements remain visible for review."""
    answers = document.get('applicationAnswers') or []
    result = []
    country = str(document.get('country') or '').strip().lower()
    if country and country not in ('us', 'usa', 'united states', 'united states of america'):
        result.append('Not US')
    checks = {name: False for name in ('US state', 'Age 18–25', 'iPhone', 'Second camera', 'Treadmill', 'Walks')}
    for answer in answers:
        label = str(answer.get('label', '')).lower()
        value = answer.get('value')
        text = str(value).strip().lower()
        negative = value is False or bool(re.search(r"\b(no|false|not|without|don't|cannot)\b", text))
        positive = value is True or text in ('true', 'yes')
        if 'age' in label or 'old are' in label:
            checks['Age 18–25'] = True
            numbers = re.findall(r'\b\d{1,3}\b', text)
            if len(numbers) == 1:
                if not 18 <= int(numbers[0]) <= 25:
                    result.append('Age outside 18–25')
            else:
                result.append('Age needs review')
        if 'state' in label or 'us based' in label:
            checks['US state'] = True
            if negative:
                result.append('Not US')
            elif text not in US_STATES:
                result.append('US state needs review')
        equipment = []
        if 'iphone' in label:
            equipment.append('iPhone')
        if 'camera' in label or '2nd' in label or 'second device' in label:
            equipment.append('Second camera')
        if 'treadmill' in label:
            equipment.append('Treadmill')
        if 'walk' in label:
            equipment.append('Walks')
        for name in equipment:
            checks[name] = True
        if any(name in equipment for name in ('iPhone', 'Second camera')):
            if negative:
                result.append('No iPhone + second camera')
            elif not positive:
                result.append('iPhone + second camera needs review')
        if any(name in equipment for name in ('Treadmill', 'Walks')):
            if negative:
                result.append('No treadmill/walks')
            elif not positive:
                result.append('Treadmill + walks needs review')
    result.extend(f'{name}: unanswered' for name, answered in checks.items() if not answered)
    return list(dict.fromkeys(result))


def identify(conn, document):
    uid = document['userId']
    saved = conn.execute('SELECT creator_id FROM sideshift_people WHERE user_id=?', (uid,)).fetchone()
    handles = []
    ids = set()
    for platform in ('tiktok', 'instagram'):
        value = document.get(platform)
        if value:
            try:
                link = parse_link(value if '://' in value else f'{platform}:{value.lstrip("@")}')
            except ValueError:  # e.g. she typed her name, "Don Baari": record it, skip only this handle
                document.setdefault('_bad_handles', []).append(f'{platform}:{value}')
                continue
            if link['kind'] != 'profile' or link['platform'] != platform:
                raise ValueError('IdentityConflict')
            handles.append((platform, link['username']))
            row = conn.execute('SELECT person_id FROM handles WHERE platform=? AND username=?',
                               handles[-1]).fetchone()
            if row:
                ids.add(row['person_id'])
    email = document.get('email')
    if email:
        email = parse_link(email)['url']
        ids.update(r['id'] for r in conn.execute('SELECT id FROM people WHERE lower(email)=?', (email,)))
    if saved:
        ids.add(saved['creator_id'])
    if len(ids) > 1:
        raise ValueError('IdentityConflict')
    cid = next(iter(ids)) if ids else intake.create(conn, document.get('name') or 'Applicant')
    for platform, username in handles:
        intake.add(conn, f'{platform}:{username}', 'external applicant', person_id=cid)
    if email:
        existing = conn.execute('SELECT email FROM people WHERE id=?', (cid,)).fetchone()['email']
        if existing and existing.lower() != email:
            raise ValueError('EmailConflict')
        intake.add(conn, email, 'external applicant', person_id=cid)
    conn.execute('INSERT OR IGNORE INTO sideshift_people VALUES (?,?)', (uid, cid))
    conn.commit()
    return cid


def plan(stage, status):
    if status == 'Accepted':
        return {'new': ['shortlist'], 'scored': ['shortlist'], 'shortlisted': []}.get(stage)
    return {s: ['declined'] for s in ('new', 'scored', 'shortlisted', 'contacted', 'followed_up', 'replied', 'negotiating')}.get(stage, [] if stage == 'declined' else None)


def finalize(conn, row, status):
    person = conn.execute('SELECT stage FROM people WHERE id=?', (row['creator_id'],)).fetchone()
    moves = plan(person['stage'], status)
    if moves is None:
        raise ValueError('PipelineConflict')
    for move in moves:
        pipeline.advance(conn, row['creator_id'], move, source='external applicant decision', job_id=row['job_id'])
    conn.execute('UPDATE sideshift_decisions SET state="done",error=NULL WHERE user_id=? AND job_id=?',
                 (row['user_id'], row['job_id']))
    conn.execute('UPDATE sideshift_applications SET status=? WHERE user_id=? AND job_id=?',
                 (status, row['user_id'], row['job_id']))
    conn.commit()


class Adapter:
    def __init__(self, client_factory=Client, platforms_factory=default_platforms):
        self.client_factory = client_factory
        self.platforms_factory = platforms_factory

    def sync(self, conn):
        setup(conn)
        conn.execute('UPDATE sideshift_health SET last_attempt=?,error=NULL', (now(),))
        conn.commit()
        try:
            client = self.client_factory()
            overview = client.request('GET', '/applicants/overview', params={'jobs': 50, 'limit': 0})['data']
            jobs = client.request('GET', '/jobs', params={'limit': 100})['data']
            if overview['totalJobs'] > len(jobs):
                raise ProtocolError('JobLimit; not all jobs accessible')
            count = 0
            research_errors = 0
            identity_errors = 0
            platforms = None
            for summary in jobs:
                jid = summary['id']
                job = client.request('GET', '/jobs/' + quote(jid, safe=''))['data']
                basic = {a['userId']: a for a in client.pages('/applicants', jobId=jid)}
                advanced = {a['userId']: a for a in client.pages('/applicants/advanced', jobId=jid, status='all')}
                if set(basic) - set(advanced):
                    raise ProtocolError('ApplicantDetailsMissing')
                for uid, applicant in advanced.items():
                    document = {**basic.get(uid, {}), **applicant}
                    try:
                        cid = identify(conn, document)
                    except ValueError as exc:  # one applicant's identity problem must not stop everyone else's sync
                        conn.rollback()
                        conn.execute('INSERT INTO sideshift_applications VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(user_id,job_id) DO UPDATE SET document=excluded.document,job=excluded.job,status=excluded.status,updated_at=excluded.updated_at,research_error=excluded.research_error',
                                     (uid, jid, json.dumps(document), json.dumps(job), '[]', document.get('status', 'Waiting Review'), now(),
                                      f'{exc}: needs identity review'))
                        conn.commit()
                        identity_errors += 1
                        count += 1
                        continue
                    posts = client.request('GET', '/applicants/top-posts', params={'userId': uid, 'jobId': jid})['data']
                    conn.execute('INSERT INTO sideshift_applications VALUES (?,?,?,?,?,?,?,NULL) ON CONFLICT(user_id,job_id) DO UPDATE SET document=excluded.document,job=excluded.job,top_posts=excluded.top_posts,status=excluded.status,updated_at=excluded.updated_at',
                                 (uid, jid, json.dumps(document), json.dumps(job), json.dumps(posts), document.get('status', 'Waiting Review'), now()))
                    conn.commit()
                    pending = conn.execute('SELECT * FROM sideshift_decisions WHERE user_id=? AND job_id=? AND state!="done"', (uid, jid)).fetchone()
                    if pending and document.get('status') == pending['status']:
                        finalize(conn, {'creator_id': cid, 'user_id': uid, 'job_id': jid}, pending['status'])
                    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
                    error = 'BadHandle ' + ', '.join(document['_bad_handles']) if document.get('_bad_handles') else None
                    for handle in conn.execute('SELECT * FROM handles WHERE person_id=?', (cid,)).fetchall():
                        latest = conn.execute('SELECT MAX(taken_at) FROM snapshots WHERE handle_id=?', (handle['id'],)).fetchone()[0]
                        if not latest or latest < cutoff:
                            try:
                                if platforms is None:
                                    platforms = self.platforms_factory()
                                snapshot.refresh(conn, handle['id'], platforms)
                            except Exception as exc:
                                error = f"{error}; {type(exc).__name__}" if error else type(exc).__name__
                    person = conn.execute('SELECT stage FROM people WHERE id=?', (cid,)).fetchone()
                    if snapshot.latest(conn, cid) and person['stage'] in ('new', 'scored'):
                        try:
                            vetting.vet(conn, cid, use_judge=False)
                        except Exception as exc:
                            error = f"{error}; {type(exc).__name__}" if error else type(exc).__name__
                    conn.execute('UPDATE sideshift_applications SET research_error=? WHERE user_id=? AND job_id=?', (error, uid, jid))
                    conn.commit()
                    research_errors += bool(error)
                    count += 1
            conn.execute('UPDATE sideshift_health SET last_sync=?,error=NULL', (now(),))
            conn.commit()
            return {'jobs': len(jobs), 'applicants': count, 'research_errors': research_errors, 'identity_errors': identity_errors}
        except MissingKey:
            conn.execute('UPDATE sideshift_health SET error="MissingKey"')
            conn.commit()
            return {'disabled': 'MissingKey'}
        except Exception as exc:
            conn.rollback()
            conn.execute('UPDATE sideshift_health SET error=?', (type(exc).__name__,))
            conn.commit()
            raise RuntimeError(f'SideShift sync: {type(exc).__name__}') from None

    def action(self, conn, route, fields):
        if route != '/extension/sideshift':
            return False
        setup(conn)
        try:
            status = {'accept': 'Accepted', 'decline': 'Declined'}[fields['do']]
            row = conn.execute('SELECT a.*,p.creator_id,c.stage,c.do_not_contact FROM sideshift_applications a JOIN sideshift_people p USING(user_id) JOIN people c ON c.id=p.creator_id WHERE user_id=? AND job_id=?',
                               (fields['user_id'], fields['job_id'])).fetchone()
            if not row or row['status'] not in ('Waiting Review', 'Viewed'):
                raise ValueError('AlreadyDecided; sync and review')
            if status == 'Accepted' and row['do_not_contact']:
                raise ValueError('DoNotContact')
            if plan(row['stage'], status) is None:
                raise ValueError('PipelineConflict')
            pending = conn.execute('SELECT 1 FROM sideshift_decisions WHERE user_id=? AND job_id=? AND state!="done"', (row['user_id'], row['job_id'])).fetchone()
            if pending:
                raise ValueError('DecisionUncertain; reconcile in SideShift and sync')
            client = self.client_factory()
            current = next((a for a in client.pages('/applicants/advanced', jobId=row['job_id'], status='all') if a['userId'] == row['user_id']), None)
            cached = json.loads(row['document'])
            if not current or any(current.get(k) != cached.get(k) for k in ('status', 'applicationAnswers', 'lastUpdated', 'tiktok', 'instagram', 'email')):
                raise ValueError('ApplicationChanged; sync and review')
            request_id = str(uuid.uuid4())
            recorded = conn.execute('INSERT INTO sideshift_decisions VALUES(?,?,?,?,"pending",NULL) ON CONFLICT(user_id,job_id) DO UPDATE SET status=excluded.status,request_id=excluded.request_id,state="pending",error=NULL WHERE sideshift_decisions.state="done"', (row['user_id'], row['job_id'], status, request_id))
            if recorded.rowcount != 1:
                conn.rollback()
                raise ValueError('DecisionUncertain; reconcile in SideShift and sync')
            conn.commit()
            result = client.request('POST', '/applicants/status', payload={'userId': row['user_id'], 'jobId': row['job_id'], 'newStatus': status}, request_id=request_id)
            if result['data'].get('success') is not True:
                raise ProtocolError('DecisionUncertain')
            finalize(conn, row, status)
            event(conn, 'external_applicant_decision', row['creator_id'], actor='owner (creator dashboard)', status=status, job_id=row['job_id'])
            conn.commit()
        except Exception as exc:
            raise RuntimeError(f'SideShift decision: {type(exc).__name__}; {str(exc) if isinstance(exc, ValueError) else "sync before retrying"}') from None
        return True

    def render(self, conn):
        setup(conn)
        health = conn.execute('SELECT * FROM sideshift_health').fetchone()
        out = ['<h2>SideShift applicants</h2>', f'<div class=card>Last sync: {escape(health["last_sync"] or "never")} · Last check: {escape(health["last_attempt"] or "never")} · {escape(health["error"] or "")}</div>']
        for row in conn.execute('SELECT a.*,p.creator_id,c.name,c.do_not_contact FROM sideshift_applications a JOIN sideshift_people p USING(user_id) JOIN people c ON c.id=p.creator_id ORDER BY a.updated_at DESC'):
            doc = json.loads(row['document'])
            score = conn.execute('SELECT score,track FROM scores WHERE person_id=? ORDER BY id DESC LIMIT 1', (row['creator_id'],)).fetchone()
            handles = ', '.join(f'{h["platform"]}:@{h["username"]}' for h in conn.execute('SELECT * FROM handles WHERE person_id=?', (row['creator_id'],)))
            out.append(f'<div class=card><a href="/person/{row["creator_id"]}">{escape(row["name"] or "Applicant")}</a> · {escape(json.loads(row["job"]).get("title", row["job_id"]))} · {escape(row["status"])}<p>{escape(handles or "No handles")} · Score: {score["score"] if score else "not available"}</p><p>{escape(" · ".join(flags(doc)))} · {escape(row["research_error"] or "")}</p>')
            for answer in doc.get('applicationAnswers') or []:
                out.append(f'<p>{escape(str(answer.get("label", "")))}: {escape(json.dumps(answer.get("value"), ensure_ascii=False))}</p>')
                if answer.get('type') == 'video' and isinstance(answer.get('value'), dict):
                    for file in answer['value'].get('files', []):
                        url = file.get('url', '')
                        if urlparse(url).scheme in ('https', 'http'):
                            out.append(f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">Watch uploaded video</a>')
            pending = conn.execute('SELECT state FROM sideshift_decisions WHERE user_id=? AND job_id=? AND state!="done"', (row['user_id'], row['job_id'])).fetchone()
            if pending:
                out.append('<b>Decision uncertain: reconcile in SideShift and sync before another decision.</b>')
            elif row['status'] in ('Waiting Review', 'Viewed'):
                out.append(f'<form method=post action="/extension/sideshift"><input type=hidden name=user_id value="{escape(row["user_id"], quote=True)}"><input type=hidden name=job_id value="{escape(row["job_id"], quote=True)}">')
                out.append('<b>Do not contact</b>' if row['do_not_contact'] else '<button name=do value=accept>Accept</button>')
                out.append('<button class=no name=do value=decline>Decline</button></form>')
            out.append('</div>')
        return ''.join(out)
