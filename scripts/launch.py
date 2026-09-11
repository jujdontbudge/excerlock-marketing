#!/usr/bin/env python3
"""Launch Pi in the ExcerLock marketing workspace."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
root = Path(__file__).resolve().parents[1]
load_dotenv(root / ".env", override=False)
os.environ.setdefault("MEM0_TELEMETRY", "0")
os.environ["PATH"] = f"{root}/.venv/bin:{Path.home()}/.local/share/agent-web/venv/bin:" + os.environ.get("PATH", "")
os.chdir(root)
os.execv(str(Path.home() / ".local/bin/pi"), ["pi", *sys.argv[1:]])
