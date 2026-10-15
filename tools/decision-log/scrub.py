"""Copy transcripts with secrets replaced by [REDACTED]. Usage: scrub.py <source dir> <output dir>"""
import re
import sys
from pathlib import Path

SECRET = re.compile(
    r'sspk_(?:live|test)_[A-Za-z0-9_-]{12,}'            # SideShift API keys
    r'|exa_[0-9a-f]{32,}'                               # excerlock-access token
    r'|\bre_[A-Za-z0-9]{8,}_[A-Za-z0-9_]{8,}'           # Resend
    r'|sk-[A-Za-z0-9_-]{16,}|AIza[0-9A-Za-z_-]{20,}'
    r'|gh[pousr]_[A-Za-z0-9]{20,}|xox[bpa]-[A-Za-z0-9-]{10,}'
    r'|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}')


def main(src, out):
    src, out = Path(src), Path(out)
    for p in src.rglob('*.jsonl'):
        target = out / p.relative_to(src)
        if target.exists() and target.stat().st_mtime >= p.stat().st_mtime:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(SECRET.sub('[REDACTED]', p.read_text(errors='replace')))


if __name__ == '__main__':
    main(*sys.argv[1:3])
