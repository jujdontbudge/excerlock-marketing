#!/usr/bin/env python3
"""Paste the small App Store card on a CTA slide (slide 4): top right, 40% of the width, rounded, soft shadow.

Usage: cta_card.py IN.png OUT.png [--side right|left]
The card is sections/slideshows/assets/appstore-card.png (the top of ExcerLock's App Store listing).
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

CARD = Path(__file__).resolve().parents[1] / "assets" / "appstore-card.png"

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst"); ap.add_argument("--side", default="right", choices=["right", "left"])
a = ap.parse_args()

bg = Image.open(a.src).convert("RGB"); W, H = bg.size
cw = int(W * 0.40)
c = Image.open(CARD).convert("RGB"); c = c.resize((cw, int(c.height * cw / c.width)), Image.LANCZOS)
r = int(cw * 0.06)
x = W - cw - int(W * 0.04) if a.side == "right" else int(W * 0.04)
y = int(H * 0.07)
mask = Image.new("L", c.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, c.width - 1, c.height - 1), r, fill=255)
sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle((x, y + 5, x + cw, y + c.height + 5), r, fill=130)
bg.paste(Image.new("RGB", (W, H)), (0, 0), sh.filter(ImageFilter.GaussianBlur(W * 0.012)))
bg.paste(c, (x, y), mask)
bg.save(a.dst)
print("card on", a.dst)
