#!/usr/bin/env python3
"""User-initiated headed login only; never called automatically by the agent."""
import argparse
import os
from pathlib import Path
from urllib.parse import urlsplit

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--headed-login', action='store_true', help='Explicitly permit opening a visible dedicated Chrome window')
parser.add_argument('url', nargs='?', default='https://example.com')
args = parser.parse_args()
if not args.headed_login:
    parser.error('No browser launched. Use --headed-login only when you want a visible login window.')
url = urlsplit(args.url)
if url.scheme not in {'http', 'https'} or not url.hostname or url.username or url.password:
    parser.error('Use an HTTP(S) URL without embedded credentials.')
profile = Path.home() / '.pi' / 'browser-profile'
if profile.is_symlink():
    parser.error('Refusing a symlinked profile; keep the agent profile separate from personal Chrome.')
profile.mkdir(mode=0o700, parents=True, exist_ok=True)
profile.chmod(0o700)
lock = profile / 'SingletonLock'
if lock.is_symlink():
    try:
        pid = int(os.readlink(lock).rsplit('-', 1)[1])
        os.kill(pid, 0)
    except ProcessLookupError:
        pass
    except (ValueError, PermissionError, IndexError):
        parser.error('Cannot establish that the profile is idle. Close its owning browser; do not delete live locks.')
    else:
        parser.error('Agent profile is in use. Exit browser-owning Pi sessions and close the dedicated browser first.')
chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
if not Path(chrome).is_file():
    parser.error('Google Chrome stable is not installed at the documented macOS path.')
print('Opening a VISIBLE dedicated login browser at ~/.pi/browser-profile. Pi settings remain headless.', flush=True)
# chrome-devtools-mcp/Puppeteer uses these flags in headless mode on macOS.
# Matching them here is required: otherwise headed Chrome encrypts cookies with
# Keychain and headless Chrome cannot decrypt those same persistent cookies.
os.execv(chrome, [
    chrome,
    f'--user-data-dir={profile}',
    '--password-store=basic',
    '--use-mock-keychain',
    '--disable-sync',
    '--no-first-run',
    '--no-default-browser-check',
    args.url,
])
