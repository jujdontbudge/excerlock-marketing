#!/usr/bin/env python3
"""Paste ExcerLock's App Store bar (icon, name, subtitle, Open button) top right on a deck's last slide,
with a small label under it.

Usage: app_icon.py IN.png OUT.png [--label "this is the app i use"] [--width 0.62]
The bar is sections/slideshows/assets/appstore-card.png. The label uses Figtree 600 (raw/fonts/Figtree.ttf),
the free stand-in for TikTok's caption font.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
CARD = ROOT / "sections/slideshows/assets/appstore-card.png"
FONT = ROOT / "raw/fonts/Figtree.ttf"

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--label", default="", help="text under the bar; the captain wants none (2026-10-06)")
ap.add_argument("--width", type=float, default=0.5, help="bar width as a share of the image width")
a = ap.parse_args()

bg = Image.open(a.src).convert("RGB"); W, H = bg.size
cw = int(W * a.width)
c = Image.open(CARD).convert("RGB"); c = c.resize((cw, int(c.height * cw / c.width)), Image.LANCZOS)
r = int(cw * 0.06)
x = W - cw - int(W * 0.04); y = int(H * 0.08)

mask = Image.new("L", c.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, c.width - 1, c.height - 1), r, fill=255)
sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle((x, y + 5, x + cw, y + c.height + 5), r, fill=130)
bg.paste(Image.new("RGB", (W, H)), (0, 0), sh.filter(ImageFilter.GaussianBlur(W * 0.012)))
bg.paste(c, (x, y), mask)

if a.label:
    f = ImageFont.truetype(str(FONT), int(W * 0.036))
    try: f.set_variation_by_axes([600])
    except Exception: pass
    d = ImageDraw.Draw(bg)
    tw = d.textlength(a.label, font=f); cx = x + cw / 2
    tx = min(max(cx - tw / 2, int(W * 0.03)), W - tw - int(W * 0.03)); ty = y + c.height + int(W * 0.025)
    d.text((tx, ty), a.label, font=f, fill="white", stroke_width=max(2, int(W * 0.004)), stroke_fill="black")
bg.save(a.dst)
print("app store bar on", a.dst)
