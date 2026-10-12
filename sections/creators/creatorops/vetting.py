"""Vetting: Jake's 20-second creator test as a score. `score` is pure; `vet` stores it; `judge` asks an AI.

Numbers (0-100):
  baseline views   0-40  median views of the last 20 posts, log scale (1k -> 10, 10k -> 25, 100k+ -> 40)
  real comments    0-30  share of sampled comments that are words or questions, not emoji/tags
  consistency      0-15  share of posts that reach at least half the median (no one-hit wonders)
  activity         0-15  posts in the last 30 days, 8+ is full marks
Track: influencer when the best median reaches ROUTING_MEDIAN (captain default 15k), else ugc.
"""
from __future__ import annotations

import json
import math
import os
import re
import shutil
import sqlite3
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .db import event, now
from .pipeline import advance
from .snapshot import latest

ROUTING_MEDIAN = int(os.environ.get("CREATORS_ROUTING_MEDIAN", 15000))


@dataclass
class Score:
    score: int
    track: str
    reasons: list[str] = field(default_factory=list)


def real_comment(text: str) -> bool:
    words = re.findall(r"[^\W\d_]{2,}", re.sub(r"@[\w.]+", "", text))
    return len(words) >= 3 or ("?" in text and len(words) >= 1)


def score(median_views: int | None, view_list: list[int], comments: list[str], posts_last_30d: int) -> Score:
    reasons = []
    mv = median_views or 0
    views_pts = round(10 * mv / 1000) if mv < 1000 else min(40, round(10 + 15 * math.log10(mv / 1000)))
    reasons.append(f"median views {mv:,} -> {views_pts}/40")
    if comments:
        share = sum(map(real_comment, comments)) / len(comments)
        comment_pts = round(30 * share)
        reasons.append(f"{share:.0%} of {len(comments)} comments are real sentences/questions -> {comment_pts}/30")
    else:
        comment_pts = 0
        reasons.append("no comments sampled -> 0/30")
    if view_list and mv:
        cons = sum(1 for v in view_list if v >= mv / 2) / len(view_list)
        cons_pts = round(15 * cons)
        reasons.append(f"{cons:.0%} of posts reach half the median -> {cons_pts}/15")
    else:
        cons_pts = 0
    act_pts = round(15 * min(posts_last_30d, 8) / 8)
    reasons.append(f"{posts_last_30d} posts in last 30 days -> {act_pts}/15")
    track = "influencer" if mv >= ROUTING_MEDIAN else "ugc"
    reasons.append(f"track {track} (influencer from {ROUTING_MEDIAN:,} median views)")
    return Score(views_pts + comment_pts + cons_pts + act_pts, track, reasons)


def _judge_cmd() -> list[str]:
    if cmd := os.environ.get("CREATORS_JUDGE_CMD"):
        return cmd.split()
    launcher = Path.home() / ".claude-api1/claude-launcher"
    return [str(launcher) if launcher.exists() else (shutil.which("claude") or "claude"), "-p", "--model", "haiku"]


JUDGE_PROMPT = """You vet creators for ExcerLock, an app that blocks the apps a user picks until they walk,
hit a step goal or go to the gym. From the bio, recent captions and comments below, answer ONLY with JSON:
{{"content_type": "talking-head|lifestyle-vlog|fitness-tutorial|dance-trend|skit|slideshow|other",
  "audience": "<who watches, 8 words max>",
  "parasocial": "strong|some|weak",
  "fit": "good|maybe|poor",
  "reason": "<one sentence>"}}

BIO: {bio}
CAPTIONS: {captions}
COMMENTS: {comments}"""


def judge(bio: str, captions: list[str], comments: list[str], run=subprocess.run) -> dict:
    """Ask a Claude agent (never a paid image key) for content type, audience and fit."""
    prompt = JUDGE_PROMPT.format(bio=bio[:500], captions=json.dumps([c[:150] for c in captions[:12]]),
                                 comments=json.dumps([c[:120] for c in comments[:40]]))
    out = run(_judge_cmd(), input=prompt, capture_output=True, text=True, timeout=300)
    m = re.search(r"\{.*\}", out.stdout, re.S)
    if out.returncode or not m:
        raise RuntimeError(f"judge failed: rc={out.returncode} {out.stderr[-300:]} {out.stdout[-300:]}")
    return json.loads(m.group(0))


def vet(conn: sqlite3.Connection, person_id: int, use_judge: bool = True) -> Score:
    snaps = latest(conn, person_id)
    if not snaps:
        raise ValueError(f"person {person_id} has no snapshot yet; refresh first")
    best = max(snaps, key=lambda s: s["median_views"] or 0)
    posts = json.loads(best["posts"])
    comments = [c for s in snaps for c in json.loads(s["comments"])]
    result = score(best["median_views"], [p["views"] for p in posts if p["views"] is not None], comments,
                   best["posts_last_30d"] or 0)
    result.reasons.insert(0, f"based on {best['platform']} @{best['username']}")
    judgement = None
    if use_judge:
        try:
            judgement = judge(best["bio"] or "", [p["caption"] for p in posts], comments)
        except Exception as e:  # the number still stands without the AI note
            judgement = {"error": str(e)[:300]}
    conn.execute("INSERT INTO scores(person_id, scored_at, score, track, reasons, judgement) VALUES (?,?,?,?,?,?)",
                 (person_id, now(), result.score, result.track, json.dumps(result.reasons),
                  json.dumps(judgement) if judgement else None))
    event(conn, "scored", person_id, score=result.score, track=result.track)
    stage = conn.execute("SELECT stage FROM people WHERE id=?", (person_id,)).fetchone()["stage"]
    if stage in ("new", "scored"):
        advance(conn, person_id, "scored")
    conn.commit()
    return result
