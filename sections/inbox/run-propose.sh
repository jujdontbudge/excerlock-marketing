#!/bin/zsh
# Inbox, propose-only, every 15 minutes (launchd com.excerlock.inbox). Claude proposes; the gate sends.
set -u
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
LOGDIR="$HOME/Library/Logs/excerlock-inbox"; mkdir -p "$LOGDIR"
LOCK="$LOGDIR/propose.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +40 2>/dev/null)" ]; then rm -rf "$LOCK"; mkdir "$LOCK"; else exit 0; fi
fi
trap 'rm -rf "$LOCK"' EXIT
cd "$REPO" && { echo "=== $(date '+%F %T') propose"; .venv/bin/python sections/inbox/propose.py; } >> "$LOGDIR/propose-$(date +%F).log" 2>&1
