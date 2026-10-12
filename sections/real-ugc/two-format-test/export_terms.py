"""Build the creator agreement that goes with the two-format brief, and optionally update its private Google Doc."""
from pathlib import Path
from typing import Any, cast
import argparse, json, subprocess
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'assets')
parser.add_argument('--sync', action='store_true', help='Update the private Google Doc (creates it the first time) and verify the readback')
args = parser.parse_args()
args.out_dir.mkdir(parents=True, exist_ok=True)
out = args.out_dir / 'two-format-agreement.docx'
ID_FILE = Path(__file__).with_name('agreement-doc-id.txt')

# Deal terms (captain, 2026-10-12). Change them here; the brief's deal box must match.
VIDEOS, PRICE, UPFRONT_PCT = 10, 150, 25
PER_VIDEO = PRICE / VIDEOS
UPFRONT = PRICE * UPFRONT_PCT / 100
CPM, BONUS_FLOOR, BONUS_DAY, CAP = 1.50, 1000, 30, 300
SPARK_DAYS = 365

INK, MUTED, ACCENT = RGBColor(0x14, 0x14, 0x14), RGBColor(0x6B, 0x6B, 0x6B), RGBColor(0xF0, 0x4E, 0x23)
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.27), Inches(11.69)
sec.top_margin = sec.bottom_margin = Inches(.55)
sec.left_margin = sec.right_margin = Inches(.75)
normal = cast(Any, doc.styles['Normal'])
normal.font.name, normal.font.size, normal.font.color.rgb = 'Nunito', Pt(11.5), INK
normal.paragraph_format.space_after = Pt(4)
normal.paragraph_format.line_spacing = 1.15


def para(text='', size=None, bold=False, color=None, after=None, before=None):
    p = doc.add_paragraph()
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


def heading(text):
    para(text.upper(), 10.5, True, ACCENT, after=2, before=10)


def item(bold, text):
    q = doc.add_paragraph(style='List Bullet')
    q.paragraph_format.space_after = Pt(3)
    run(q, bold, bold=True)
    run(q, text)


money = lambda x: f'${x:,.2f}'.replace('.00', '')

para('EXCERLOCK  ·  CREATOR AGREEMENT', 10, True, ACCENT, after=0)
para('Your deal, in plain words', 24, True, INK, after=4)
para('This goes with your creator brief. It covers what you make, when, how you get paid and what we can do with your videos. When you sign it on your creator page, we have a deal.', 12, color=MUTED, after=4)

heading('What you make')
item('10 different videos ', f'in the two formats from your brief, 10 to 20 seconds each, vertical 9:16.')
item('Post them ', 'on TikTok and Instagram Reels, on your own account or on a fresh account we warm up with you.')
item('Hand them in ', 'on your creator page: the final video, the raw clips you filmed for it, and the post links once they are live.')

heading('When')
item('Week 1: ', '5 videos posted within 7 days of signing.')
item('Week 2: ', 'the other 5 posted within 14 days of signing.')
item('Drafts first. ', 'Send each draft on your creator page before you post. We reply within 24 hours. No reply in 24 hours means go ahead and post.')

heading('How you get paid')
item(f'{money(PRICE)} for all 10 videos', f' ({money(PER_VIDEO)} a video).')
item(f'{money(UPFRONT)} when you sign ', f'({UPFRONT_PCT}%), so you are paid before you film.')
item('The rest when your videos are in. ', f'We pay {money(PER_VIDEO)} for every video you deliver, minus the {money(UPFRONT)} you already have.')
item('View bonus. ', f'Once a video passes {BONUS_FLOOR:,} views, it earns {money(CPM)} for every 1,000 views, counted {BONUS_DAY} days after you post. Each video can earn up to {money(CAP)} per platform, including its {money(PER_VIDEO)} share of the base. TikTok and Reels count separately. We pay it after the 30-day count.')
item('Paid by ', 'PayPal or Wise. Add your details on your creator page.')

heading('What we can do with your videos')
para('We want to run your best videos as ads and keep using them, and that is all included in your fee:', after=3)
item('Forever, anywhere. ', 'You give ExcerLock a permanent, worldwide right to use your videos, raw clips, name, voice and face in our marketing. That covers our own accounts, our website and app store pages, and paid ads on any platform.')
item('Edits. ', 'We can trim, re-caption, add text or music, and cut new versions from your raw clips.')
item('Spark and partnership ads. ', f'For every video on your account, send us a TikTok Spark Ads code set to {SPARK_DAYS} days and accept our Instagram partnership-ad request, within 2 days of posting.')
item('Keep them up. ', 'Leave every video public on your account. Deleting or hiding one stops the ads running from it.')
item('Your portfolio. ', 'You can always show the videos in your own portfolio.')

heading('If plans change')
item('Running late? ', 'Tell us. If we hear nothing from you for 3 days, we can end the deal.')
item('If the deal ends early, ', f'we pay {money(PER_VIDEO)} for each video you delivered, and the {money(UPFRONT)} upfront counts toward it. Everything you delivered stays covered by this agreement.')

para('Questions before you sign? Reply to our email and we will sort it out.', 11, color=MUTED, before=10)
doc.save(str(out))
print(f'Local agreement: {out}')
if not args.sync:
    raise SystemExit(0)

name = 'ExcerLock creator agreement'
if ID_FILE.exists():
    identity = ID_FILE.read_text().strip()
    cmd = ['gws', 'drive', 'files', 'update', '--json', json.dumps({'name': name}), '--upload', str(out),
           '--upload-content-type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
           '--params', json.dumps({'fileId': identity, 'fields': 'id'})]
else:
    cmd = ['gws', 'drive', 'files', 'create', '--json', json.dumps({'name': name, 'mimeType': 'application/vnd.google-apps.document'}),
           '--upload', str(out), '--upload-content-type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
           '--params', json.dumps({'fields': 'id'})]
identity = json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)['id']
ID_FILE.write_text(identity + '\n')
for mime, fname in [('text/plain', 'two-format-agreement-readback.txt'), ('application/pdf', 'two-format-agreement.pdf')]:
    subprocess.run(['gws', 'drive', 'files', 'export', '--params', json.dumps({'fileId': identity, 'mimeType': mime}), '--output', str(args.out_dir / fname)], check=True, capture_output=True)
readback = (args.out_dir / 'two-format-agreement-readback.txt').read_text()
for must in ['WHAT YOU MAKE', 'WHEN', 'HOW YOU GET PAID', 'WHAT WE CAN DO WITH YOUR VIDEOS', 'IF PLANS CHANGE', money(PRICE), f'{SPARK_DAYS} days', 'permanent, worldwide']:
    assert must in readback, must
print(f'Verified Google Doc {identity}: https://docs.google.com/document/d/{identity}/edit')
