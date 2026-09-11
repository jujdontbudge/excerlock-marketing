#!/usr/bin/env python3
"""Free TikTok metadata collector using TikTokApi; writes JSON without downloading media."""
import argparse
import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from TikTokApi import TikTokApi

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="mode", required=True)
    for mode in ("trending", "hashtag", "user"):
        q = sub.add_parser(mode)
        if mode != "trending":
            q.add_argument("target", help="hashtag without # or TikTok username")
        q.add_argument("--count", type=int, default=30)
        q.add_argument("--out", required=True)
    return p.parse_args()


async def collect(args):
    if not 1 <= args.count <= 100:
        raise SystemExit("--count must be between 1 and 100")
    token = os.environ.get("TIKTOK_MS_TOKEN")
    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1,
            ms_tokens=[token] if token else None,
            headless=True,
            sleep_after=3,
            suppress_resource_load_types=["image", "media", "font"],
        )
        if args.mode == "trending":
            stream = api.trending.videos(count=args.count)
        elif args.mode == "hashtag":
            stream = api.hashtag(name=args.target.lstrip("#")).videos(count=args.count)
        else:
            stream = api.user(username=args.target.lstrip("@")).videos(count=args.count)
        records = []
        async for video in stream:
            records.append(video.as_dict)
            if len(records) >= args.count:
                break
        return records


def main():
    args = parse_args()
    out = Path(args.out)
    if out.exists():
        raise SystemExit(f"Refusing to overwrite: {out}")
    try:
        records = asyncio.run(collect(args))
    except Exception as exc:
        raise SystemExit(f"TikTok collection failed: {type(exc).__name__}: {exc}") from exc
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"mode": args.mode, "target": getattr(args, "target", None), "count": len(records), "items": records}, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(out), "count": len(records)}))


if __name__ == "__main__":
    main()
