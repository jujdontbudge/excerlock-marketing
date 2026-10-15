#!/bin/zsh
# Contract flow every 15 minutes (launchd com.excerlock.flow). It only proposes; the gate sends.
set -u
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
LOGDIR="$HOME/Library/Logs/excerlock-inbox"; mkdir -p "$LOGDIR"
cd "$REPO" && { echo "=== $(date '+%F %T') flow"; .venv/bin/python sections/inbox/flow.py; } >> "$LOGDIR/flow-$(date +%F).log" 2>&1
