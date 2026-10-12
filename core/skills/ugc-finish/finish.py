#!/usr/bin/env python3
"""Make a finished image or video look like real phone UGC before it goes to TikTok.

Every file gets, in order:
  1. light luma noise using the requested 2-3 grain setting;
  2. an export capped at 1080 px on the short side, without upscaling;
  3. source metadata stripping and a local compression approximation, or an authorized messaging round trip.

Step 3 has two routes:
  --telegram  really sends the file through Telegram as a photo/video and downloads Telegram's
              recompressed copy. Needs TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in the environment.
  default     is a local approximation, not a verified Telegram round trip: JPEG quality 82
              with 4:2:0 chroma for images, H.264 CRF 26 + AAC for video, metadata stripped.

Usage: finish.py IN [IN ...] --out DIR [--grain 2.5] [--telegram]
Outputs are JPEG for images, MP4 for videos, same base name.
"""
import argparse, hashlib, json, os, random, subprocess, sys, urllib.request, uuid
from pathlib import Path
from PIL import Image, ImageOps

VIDEO = {".mp4", ".mov", ".m4v", ".webm"}


def secret(name):
    return os.environ.get(name) or None


def grain_image(im, pct):
    """Add light monochrome noise; sigma=pct*1.2 levels, not a calibrated CapCut equivalence."""
    import numpy as np
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    rng = np.random.default_rng(random.randrange(1 << 30))
    noise = rng.normal(0, pct * 1.2, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a + noise, 0, 255).astype("uint8"))


def to_1080(im):
    w, h = im.size
    s = min(1, 1080 / min(w, h))
    return im.resize((round(w * s), round(h * s)), Image.LANCZOS)


def finish_image(src, dst, pct):
    with Image.open(src) as source:
        im = to_1080(ImageOps.exif_transpose(source).convert("RGB"))
    im = grain_image(im, pct)
    with Path(dst).open("xb") as stream:
        im.save(stream, "JPEG", quality=82, subsampling="4:2:0", optimize=True)


def finish_video(src, dst, pct):
    strength = max(1, round(pct * 2))  # ffmpeg uniform noise, matched by eye to the image grain
    vf = (f"scale=w='trunc(iw*min(1,1080/min(iw,ih))/2)*2':h='trunc(ih*min(1,1080/min(iw,ih))/2)*2':flags=lanczos,"
          f"noise=c0s={strength}:c0f=t+u,format=yuv420p")
    subprocess.run(["ffmpeg", "-n", "-loglevel", "error", "-i", str(src), "-vf", vf,
                    "-c:v", "libx264", "-preset", "medium", "-crf", "26", "-r", "30",
                    "-c:a", "aac", "-b:a", "128k", "-map_metadata", "-1", "-map_chapters", "-1",
                    "-metadata", "creation_time=", "-fflags", "+bitexact", "-flags:v", "+bitexact",
                    "-flags:a", "+bitexact", "-movflags", "+faststart", str(dst)], check=True)


def telegram_roundtrip(path, is_video, chat):
    tok = secret("TELEGRAM_BOT_TOKEN")
    if not (tok and chat):
        raise ValueError("Telegram requires an authorized explicit chat ID and bot credential")
    kind = "video" if is_video else "photo"
    b = uuid.uuid4().hex
    data = path.read_bytes()
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{chat}\r\n"
            f"--{b}\r\nContent-Disposition: form-data; name=\"{kind}\"; filename=\"{path.name}\"\r\n"
            f"Content-Type: application/octet-stream\r\n\r\n").encode() + data + f"\r\n--{b}--\r\n".encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{tok}/send{kind.title()}", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    msg = json.load(urllib.request.urlopen(req, timeout=300))["result"]
    fid = (msg["video"] if is_video else max(msg["photo"], key=lambda p: p["width"] * p["height"]))["file_id"]
    fp = json.load(urllib.request.urlopen(f"https://api.telegram.org/bot{tok}/getFile?file_id={fid}", timeout=60))["result"]["file_path"]
    returned = urllib.request.urlopen(f"https://api.telegram.org/file/bot{tok}/{fp}", timeout=300).read()
    if not returned:
        raise ValueError("Telegram returned an empty file")
    path.write_bytes(returned)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--grain", type=float, default=2.5, help="percent, keep between 2 and 3")
    ap.add_argument("--telegram", action="store_true")
    ap.add_argument("--chat-id", help="Explicit authorized destination; no fallback to another bot's chat")
    a = ap.parse_args()
    if not 2 <= a.grain <= 3:
        sys.exit("grain must be 2-3%")
    if a.telegram and not a.chat_id:
        sys.exit("--telegram requires --chat-id for an authorized destination")
    out = Path(a.out)
    planned = []
    for s in map(Path, a.inputs):
        vid = s.suffix.lower() in VIDEO
        d = out / (s.stem + (".mp4" if vid else ".jpg"))
        if not s.is_file() or s.stat().st_size == 0:
            sys.exit("Missing or empty input")
        if s.with_suffix(s.suffix + ".finish.json").exists():
            sys.exit("Input was already finished; use the approved original")
        if d.exists() or d.is_symlink() or d.with_suffix(d.suffix + ".finish.json").exists():
            sys.exit("Refusing to overwrite finished output")
        if any(p[1].resolve() == d.resolve() for p in planned):
            sys.exit("Inputs have colliding output names")
        planned.append((s, d, vid))
    out.mkdir(parents=True, exist_ok=True)
    for s, d, vid in planned:
        (finish_video if vid else finish_image)(s, d, a.grain)
        if a.telegram:
            try:
                telegram_roundtrip(d, vid, a.chat_id)
            except Exception:
                sys.exit("Telegram round trip failed; local file is not verified for handoff")
        if vid:
            subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", str(d)], check=True, capture_output=True)
        else:
            with Image.open(d) as image:
                image.verify()
        receipt = {"source": str(s), "source_sha256": hashlib.sha256(s.read_bytes()).hexdigest(),
                   "output_sha256": hashlib.sha256(d.read_bytes()).hexdigest(), "grain": a.grain,
                   "route": "telegram" if a.telegram else "local-approximation"}
        with d.with_suffix(d.suffix + ".finish.json").open("x") as stream:
            json.dump(receipt, stream, indent=2)
        print("finished", d, "(telegram)" if a.telegram else "(local)")


if __name__ == "__main__":
    main()
