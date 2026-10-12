"""Create a private Google Docs working draft from current confirmed inputs."""
from pathlib import Path
from typing import Any, cast
import json, subprocess
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'assets')
parser.add_argument('--sync', action='store_true', help='Update the existing private Google Doc; verifies exact-target exports')
args = parser.parse_args()
base = args.out_dir
base.mkdir(parents=True, exist_ok=True)
out = base / 'two-format-working-draft.docx'

INK, MUTED, ACCENT, PANEL = RGBColor(0x14, 0x14, 0x14), RGBColor(0x6B, 0x6B, 0x6B), RGBColor(0xF0, 0x4E, 0x23), 'F4F4F2'
HAYDEN = 'https://www.tiktok.com/@haydenn.fit/video/7692111837885664543'
WALKING = 'https://www.tiktok.com/@walking.w.ry/video/7603509206842428703'
REACTION_REFS = [  # captain's picks from raw/briefs/reference-review, re-hosted on Drive (no X links)
    ('https://drive.google.com/file/d/1hQvOf5IXCbGOTMnekAuF8xX7gkmL-o8M/view', 'Reaction A'),
    ('https://drive.google.com/file/d/18xPODE6Yt9Wht5TJSXVKQoNQCqWz3G6p/view', 'Reaction B'),
]

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.27), Inches(11.69)
sec.top_margin = sec.bottom_margin = Inches(.4)
sec.left_margin = sec.right_margin = Inches(.7)
normal = cast(Any, doc.styles['Normal'])
normal.font.name, normal.font.size, normal.font.color.rgb = 'Nunito', Pt(11.5), INK
normal.paragraph_format.space_after = Pt(4)
normal.paragraph_format.line_spacing = 1.15


def para(text='', size=None, bold=False, color=None, after=None, before=None, container=None):
    p = (container or doc).add_paragraph()
    if text:
        run(p, text, size, bold, color)
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    if before is not None:
        p.paragraph_format.space_before = Pt(before)
    return p


def run(p, text, size=None, bold=False, color=None):
    r = p.add_run(text)
    r.bold = bold
    if size:
        r.font.size = Pt(size)
    if color is not None:
        r.font.color.rgb = color
    return r


def link(p, url, label=None):
    rel = p.part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    h = OxmlElement('w:hyperlink'); h.set(qn('r:id'), rel)
    r = OxmlElement('w:r'); rpr = OxmlElement('w:rPr')
    c = OxmlElement('w:color'); c.set(qn('w:val'), 'F04E23'); rpr.append(c)
    u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); rpr.append(u)
    r.append(rpr); t = OxmlElement('w:t'); t.text = label or url; r.append(t); h.append(r)
    p._p.append(h)


def shade(cell, fill):
    pr = cell._tc.get_or_add_tcPr(); s = OxmlElement('w:shd')
    s.set(qn('w:val'), 'clear'); s.set(qn('w:color'), 'auto'); s.set(qn('w:fill'), fill); pr.append(s)


def pad(table, top=80, side=140):
    mar = OxmlElement('w:tblCellMar')
    for edge, v in (('top', top), ('bottom', top), ('left', side), ('right', side)):
        e = OxmlElement(f'w:{edge}'); e.set(qn('w:w'), str(v)); e.set(qn('w:type'), 'dxa'); mar.append(e)
    table._tbl.tblPr.append(mar)


def widths(table, *inches):
    table.autofit = False
    for col, w in zip(table.columns, inches):
        col.width = Inches(w)
        for cell in col.cells:
            cell.width = Inches(w)


def no_borders(table):
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement(f'w:{edge}'); e.set(qn('w:val'), 'nil'); borders.append(e)
    table._tbl.tblPr.append(borders)


def heading(text):
    para(text.upper(), 10.5, True, ACCENT, after=2, before=7)


def panel():
    t = doc.add_table(rows=1, cols=1); no_borders(t); pad(t, 110, 180); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    widths(t, 7.07)
    c = t.cell(0, 0); shade(c, PANEL); c.paragraphs[0].paragraph_format.space_after = Pt(2)
    return c


para('EXCERLOCK  ·  CREATOR BRIEF', 10, True, ACCENT, after=0)
para('Two easy formats, 10 videos', 26, True, INK, after=4)
para('ExcerLock locks the apps you pick until you move. Walk and they open, stop and they lock. Your videos show that.', 12.5, color=MUTED, after=4)

heading('The deal')
for label, value in [
    ('Pay: ', '$150 for 10 different videos, $37.50 of it when you sign. Each takes 3 to 5 minutes.'),
    ('Bonus: ', '$1.50 per 1,000 views once a video passes 1,000 views, counted at 30 days. Up to $300 per video on each platform.'),
    ('When: ', '5 videos in week one, 5 in week two. Full terms are in your creator agreement.'),
    ('Where: ', 'TikTok and Instagram Reels, on your account or a fresh one we warm up with you.'),
]:
    q = para(after=2); run(q, label, bold=True); run(q, value)

heading('1. Campaign objective')
para('After watching this video, the viewer should believe ExcerLock is the missing tool that turns her phone habit into more steps and more gym days.')

heading('2. Key product messaging')
for text in ['Your phone habit becomes the reason you move.', 'Hitting your steps and getting to the gym gets easier to stick to.', 'It helps whether you are starting out or already making progress.']:
    q = doc.add_paragraph(style='List Bullet'); q.paragraph_format.space_after = Pt(2); run(q, text)

heading('3. Target audience insights')
for bold, text in [
    ('Who: ', 'girls and women 16 to 30 into walking, step counts, the gym and their goal body.'),
    ('Behaviors: ', 'on their phone all day, so the walk or the gym keeps getting pushed back.'),
    ('Apps they already use: ', 'TikTok and Instagram.'),
]:
    q = para(after=2); run(q, bold, bold=True); run(q, text)

heading('4. Content requirements')
para('TikTok and Instagram Reels, 10 to 20 seconds, vertical 9:16. Film it all yourself, use our hook and text word for word, and send us the draft before you post. We reply within 24 hours.')

heading('5. The formats and creative inspiration')
para('Format 1 · Reaction demo', 14, True, INK, after=3, before=2)
para('Start on your face, shocked, with the hook on screen. Then scroll while you walk and your apps stay open. Stop walking and they lock. Walk again and they open. React to it every time. Have a friend film you on a second phone, or prop one up and film yourself.')
q = para(after=2); run(q, 'Branding moment: ', bold=True); run(q, 'your screen locking and unlocking.')
q = para(after=8); run(q, 'Watch: ', bold=True)
link(q, REACTION_REFS[0][0], REACTION_REFS[0][1]); run(q, ' (shocked face, then the phone)  ·  ')
link(q, REACTION_REFS[1][0], REACTION_REFS[1][1]); run(q, ' (reaction, then the app)')

para('Format 2 · POV walking with text', 14, True, INK, after=3)
para('Prop your phone on the counter for one wide shot. Walk laps around your kitchen while you scroll, with text on screen the whole time, something like:', after=2)
para('"dream body hack: get an app that doesnt let you scroll unless your walking"', bold=True, after=4)
q = para(after=2); run(q, 'Branding moment: ', bold=True); run(q, 'none. Keep the ExcerLock name off the screen.')
q = para(after=2); run(q, 'Watch: ', bold=True)
link(q, HAYDEN, 'Hayden on TikTok'); run(q, ' (copy this exact video)  ·  ')
link(q, WALKING, '@walking.w.ry'); run(q, ' (how to hold the phone)')

doc.save(str(out))
print(f"Local brief: {out}")
if not args.sync:
    raise SystemExit(0)
identity = '1GfeqoP9he9kZlnPoWoIJNn9swWoCp7VAlEwGcDfCA7Q'
metadata = {'name': 'ExcerLock creator brief: two formats, 10 videos', 'description': 'Creator brief draft for captain review.'}
cmd = ['gws', 'drive', 'files', 'update', '--json', json.dumps(metadata), '--upload', str(out), '--upload-content-type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '--params', json.dumps({'fileId': identity, 'fields': 'id,name,mimeType,webViewLink'})]
result = subprocess.run(cmd, capture_output=True, text=True, check=True)
assert json.loads(result.stdout)['id'] == identity
for mime, name in [('text/plain', 'two-format-google-doc-readback.txt'), ('application/pdf', 'two-format-google-doc.pdf')]:
    subprocess.run(['gws', 'drive', 'files', 'export', '--params', json.dumps({'fileId': identity, 'mimeType': mime}), '--output', str(base / name)], check=True)
readback = (base / 'two-format-google-doc-readback.txt').read_text()
assert all(h in readback for h in ['THE DEAL', '1. CAMPAIGN OBJECTIVE', '2. KEY PRODUCT MESSAGING', '3. TARGET AUDIENCE INSIGHTS', '4. CONTENT REQUIREMENTS', '5. THE FORMATS AND CREATIVE INSPIRATION'])
assert '$150 for 10 different videos' in readback
assert 'Film it all yourself' in readback
assert 'x.com' not in readback
import pymupdf
with pymupdf.open(base / 'two-format-google-doc.pdf') as pdf:
    assert len(pdf) == 1, f'Brief exceeded one page: {len(pdf)}'
print('Verified exact Google Doc ID, content and one-page PDF.')
