"""Compose the optional contacts integration with the creator dashboard/jobs."""
import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "sections/creators"))
load_dotenv(ROOT / ".env", override=False)

from creatorops.db import connect
from connector import InboxAdapter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("sync", "jobs", "serve"))
    parser.add_argument("--db", help="Creator store path (same as creators --db)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    adapter = InboxAdapter()
    if args.command == "serve":
        from creatorops.dashboard import serve
        return serve(args.db, args.host, args.port, extensions=(adapter,))
    with connect(args.db) as conn:
        result = {"contacts_mcp": adapter.sync(conn)}
        if args.command == "jobs":
            from creatorops.channels import default_channels
            from creatorops.jobs import run
            from creatorops.platforms import default_platforms
            result["creators"] = run(conn, default_platforms(), default_channels())
        print(json.dumps(result))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"contacts connector failed ({type(exc).__name__})", file=sys.stderr)
        sys.exit(1)
