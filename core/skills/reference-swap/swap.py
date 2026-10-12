#!/usr/bin/env python3
"""One authorized image roll; exclusive outputs and a per-image attempt ledger.

--dry-run validates inputs without credentials, spend or writes. Actual calls need
--approval, --estimated-cost and --state (reuse that ledger across reference/prompt
changes for the same image). A higher size or fourth attempt needs an explicit
--exception-approval. Approval flags record user authorization, not grant it.
"""
import argparse, base64, fcntl, hashlib, io, json, math, mimetypes, os, sys
import urllib.error, urllib.request
from contextlib import contextmanager
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
MODELS = {"pro": "gemini-3-pro-image", "flash": "gemini-3.1-flash-image"}
RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]


def parser():
    ap = argparse.ArgumentParser(description=__doc__)
    for field in ("prompt", "out", "ref"):
        ap.add_argument("--" + field, type=Path, required=True)
    ap.add_argument("--face", type=Path)
    ap.add_argument("-n", type=int, default=1, choices=[1])
    ap.add_argument("--model", default="pro", choices=list(MODELS))
    ap.add_argument("--size", default="1K", choices=["1K", "2K", "4K"])
    ap.add_argument("--aspect", choices=RATIOS)
    ap.add_argument("--state", type=Path)
    ap.add_argument("--approval")
    ap.add_argument("--exception-approval")
    ap.add_argument("--estimated-cost", type=float)
    ap.add_argument("--dry-run", action="store_true")
    return ap


def credentials():
    key = os.environ.get("GEMINI_API_KEY")
    if not key and (ROOT / ".env").exists():
        for line in (ROOT / ".env").read_text().splitlines():
            if line.startswith("GEMINI_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('\"\'')
                break
    if not key:
        raise ValueError("Image-generation credential missing")
    return key


def validate(a, attempts=0):
    if a.out.exists() or a.out.is_symlink():
        raise FileExistsError("Output already exists; choose a new roll path")
    if a.out.suffix.lower() != ".png":
        raise ValueError("Output must be a PNG path")
    if a.size != "1K" or attempts >= 3:
        if not a.exception_approval or not a.exception_approval.strip():
            raise ValueError("Above 1K or three attempts requires exception approval")
    if not a.dry_run:
        if not a.approval or not a.approval.strip() or not a.state:
            raise ValueError("Actual calls require approval and a stable per-image state path")
        if a.estimated_cost is None or not math.isfinite(a.estimated_cost) or a.estimated_cost <= 0:
            raise ValueError("Record a positive finite estimated cost before submission")
        if a.state.resolve() in {p.resolve() for p in (a.out, a.ref, a.prompt, a.face) if p}:
            raise ValueError("State path must be separate from inputs and output")


def payload(a):
    with Image.open(a.ref) as im:
        w, h = im.size
        im.verify()
    aspect = a.aspect or min(RATIOS, key=lambda r: abs(int(r.split(":")[0]) / int(r.split(":")[1]) - w / h))
    parts = []
    for i, path in enumerate([p for p in (a.ref, a.face) if p], 1):
        with Image.open(path) as im:
            im.verify()
        parts.extend([{"text": f"Image {i}:"}, {"inline_data": {
            "mime_type": mimetypes.guess_type(path)[0] or "image/jpeg",
            "data": base64.b64encode(path.read_bytes()).decode()}}])
    prompt = a.prompt.read_text()
    if not prompt.strip():
        raise ValueError("Prompt is empty")
    parts.append({"text": prompt})
    return aspect, json.dumps({"contents": [{"role": "user", "parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE"],
        "imageConfig": {"aspectRatio": aspect, "imageSize": a.size}}}).encode()


def request_image(a, body, key):
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODELS[a.model]}:generateContent",
        data=body, headers={"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=300) as response:
        result = json.load(response)
    for candidate in result.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            data = part.get("inlineData") or part.get("inline_data")
            if data and data.get("mimeType", data.get("mime_type", "")).startswith("image/"):
                raw = base64.b64decode(data["data"], validate=True)
                with Image.open(io.BytesIO(raw)) as im:
                    im.load()
                    encoded = io.BytesIO()
                    im.save(encoded, "PNG")
                return encoded.getvalue()
    raise ValueError("Provider returned no image")


def save_state(path, records):
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    with tmp.open("x") as stream:
        json.dump({"attempts": records}, stream, indent=2)
    os.replace(tmp, path)


def read_attempts(path):
    records = json.loads(path.read_text())["attempts"] if path and path.exists() else []
    if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
        raise ValueError("Attempt ledger is malformed")
    return records


@contextmanager
def project_roll_lock():
    folder = ROOT / "raw"
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "reference-swap-roll.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def execute(a):
    validate(a, len(read_attempts(a.state)) if a.dry_run else 0)
    aspect, body = payload(a)
    if a.dry_run:
        return {"status": "dry-run", "aspect": aspect, "model": MODELS[a.model], "size": a.size, "out": str(a.out)}
    a.state.parent.mkdir(parents=True, exist_ok=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with project_roll_lock(), a.state.with_suffix(a.state.suffix + ".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        records = read_attempts(a.state)
        validate(a, len(records))
        key = credentials()
        entry = {"out": str(a.out), "model": MODELS[a.model], "size": a.size,
            "approval": a.approval, "exception_approval": a.exception_approval,
            "estimated_cost": a.estimated_cost, "status": "submitted"}
        records.append(entry)
        save_state(a.state, records)  # Count failed/uncertain submissions too; never retry blindly.
        try:
            image = request_image(a, body, key)
            with a.out.open("xb") as stream:
                stream.write(image)
            entry.update(status="saved", sha256=hashlib.sha256(image).hexdigest())
        except Exception as error:
            entry.update(status="failed", error=type(error).__name__)
            raise
        finally:
            save_state(a.state, records)
    return {"status": "saved", "out": str(a.out), "attempt": len(records), "sha256": entry["sha256"]}


def main(argv=None):
    a = parser().parse_args(argv)
    try:
        print(json.dumps(execute(a)))
        return 0
    except Exception as error:
        # Don't print provider bodies or exception URLs: they can contain sensitive data.
        message = str(error) if isinstance(error, (ValueError, FileExistsError)) else type(error).__name__
        print(json.dumps({"status": "failed", "error": message}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
