"""Compose optional applicant and message adapters with creator jobs/dashboard."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'sections/creators'))
load_dotenv(ROOT / '.env', override=False)

from creatorops.db import connect
from adapter import Adapter


def gate_panel():
    """The inbox gate's 'Needs you' panel (integrations/inbox-gate/panel.py), if present."""
    path = ROOT / 'integrations/inbox-gate/panel.py'
    if not path.exists():
        return []
    spec = importlib.util.spec_from_file_location('inbox_gate_panel', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return [module.GatePanel()]


def extensions(contacts=False):
    adapters = [Adapter()]
    if contacts:
        # The existing adapter uses a sibling `client` import. Bind it while loading
        # without allowing its module name to shadow this adapter's HTTP client.
        directory = ROOT / 'integrations/contacts-mcp'
        previous = sys.modules.get('client')
        try:
            spec = importlib.util.spec_from_file_location('client', directory / 'client.py')
            module = importlib.util.module_from_spec(spec)
            sys.modules['client'] = module
            spec.loader.exec_module(module)
            spec = importlib.util.spec_from_file_location('contacts_connector', directory / 'connector.py')
            connector = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(connector)
            adapters.append(connector.InboxAdapter())
        finally:
            if previous is None:
                sys.modules.pop('client', None)
            else:
                sys.modules['client'] = previous
    return adapters + gate_panel()  # last: run.py addresses adapters[0] and adapters[1] by position


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('sync', 'jobs', 'serve'))
    parser.add_argument('--db')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=8765, type=int)
    parser.add_argument('--contacts', action='store_true', help='Also compose existing contacts messages')
    args = parser.parse_args()
    adapters = extensions(args.contacts)
    if args.command == 'serve':
        from creatorops.dashboard import serve
        return serve(args.db, args.host, args.port, extensions=adapters)
    with connect(args.db) as conn:
        result = {'sideshift': adapters[0].sync(conn)}
        if args.contacts:
            result['contacts_mcp'] = adapters[1].sync(conn)
        if args.command == 'jobs':
            from creatorops.jobs import run
            from creatorops.channels import default_channels
            from creatorops.platforms import default_platforms
            result['creators'] = run(conn, default_platforms(), default_channels())
        print(json.dumps(result))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'SideShift command failed ({type(exc).__name__})', file=sys.stderr)
        sys.exit(1)
