#!/bin/zsh
# Copy this Mac's (the Air's) Claude Code transcripts for this repo to the Pro, where the decision log
# (declog.py, launchd com.excerlock.decision-log) archives them and extracts the captain's decisions.
# Secrets are scrubbed BEFORE anything leaves the Air (2026-10-15: a SideShift key once appeared in a screen read).
# Append-only copy (never deletes). launchd: com.excerlock.transcript-mirror, every 30 min.
set -u
DIR="$HOME/.claude/projects/-Users-johansardar-excerlockmarketing"
OUT="$HOME/Library/Caches/excerlock-transcript-mirror"
/usr/bin/python3 "$(dirname "$0")/scrub.py" "$DIR" "$OUT" || exit 1
ssh -o ConnectTimeout=10 -o BatchMode=yes pro "mkdir -p '$DIR'" || exit 0
rsync -a --include='*/' --include='*.jsonl' --exclude='*' "$OUT/" "pro:$DIR/" && echo "$(date '+%F %T') mirrored (scrubbed)" >> "$HOME/Library/Logs/excerlock-transcript-mirror.log"
