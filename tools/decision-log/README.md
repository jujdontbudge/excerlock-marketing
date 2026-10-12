# Decision history

Implementation owner: `tools/decision-log/declog.py`. It archives source transcripts, extracts attributable events and renders cold readable views. Its event labels are historical evidence, not operative policy; check canonical files before acting.

- `log/events.jsonl`: source events, tracked.
- `log/transcripts/`: numbered, redacted gzipped source records, ignored.
- `log/work/`: watcher state, ignored.
- `log/views/`: regenerated timelines, ignored; absent in a fresh checkout until render.

Read commands from the repo root:
- `tools/decision-log/declog.py status`
- `tools/decision-log/declog.py read <session>#<start>-<end>`
- `tools/decision-log/declog.py search <words>`
- `tools/decision-log/declog.py render`: rebuild views without extraction agents.

`run` archives and extracts new material using a subscription agent before rendering; it is not needed just to read history. The existing macOS launch agent `com.excerlock.decision-log` runs every 30 minutes while the Mac is awake. Its schedule was preserved during cleanup.

The extractor can misread short corrections or leave obsolete questions marked open. Promote confirmed procedures into their canonical homes; preserve source/correction chains. Never replace a user's stated reason with inference. Secrets are redacted before archives are persisted; historical output is not evidence that every possible secret pattern is covered.
