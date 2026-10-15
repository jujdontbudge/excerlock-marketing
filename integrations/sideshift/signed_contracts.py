"""Print the signed SideShift contracts for one campaign as JSON, for the inbox run.

Read-only: GET /contracts only. Uses SIDESHIFT_CONTRACTS_KEY from the root .env, a key whose only permission
is "View contracts" (created 2026-10-14), so the inbox run can't change anything in SideShift.
Usage: .venv/bin/python integrations/sideshift/signed_contracts.py <campaignId>
Prints [{"contractId", "status", "creatorId", "creatorName", "signedAt"}] for contracts the
creator has signed; on failure prints {"error": "<safe class>"} and exits 1.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import os  # noqa: E402

from dotenv import load_dotenv  # noqa: E402

load_dotenv(Path(__file__).resolve().parents[2] / '.env')
from client import APIError, Client  # noqa: E402

SIGNED = {'active', 'completed', 'expired', 'ended'}  # SideShift: pending until the creator accepts, then active
UNSIGNED = {'draft', 'pending', 'invited', 'sent', 'awaiting_signature', 'cancelled', 'canceled',
            'declined', 'expired', 'rejected'}


def first(doc, *names):
    for name in names:
        value = doc.get(name)
        if value:
            return value
    return None


def summarise(contract):
    creator = contract.get('creator') if isinstance(contract.get('creator'), dict) else {}
    return {
        'contractId': contract.get('id'),
        'status': str(contract.get('status') or '').lower(),
        'creatorId': first(contract, 'contractorId', 'creatorId', 'creatorUserId', 'userId') or first(creator, 'id', 'userId'),
        'creatorName': first(creator, 'name', 'displayName', 'firstName') or first(contract, 'contractorName', 'creatorName'),
        'signedAt': first(contract, 'creatorSignedAt', 'signedAt', 'acceptedAt', 'activatedAt'),
    }


def main(campaign_id):
    try:
        contracts = [summarise(c) for c in Client(os.environ.get('SIDESHIFT_CONTRACTS_KEY')).pages('/contracts', programId=campaign_id)]
    except APIError as error:
        print(json.dumps({'error': str(error)}))
        return 1
    print(json.dumps([c for c in contracts if c['signedAt'] or c['status'] in SIGNED or (c['status'] and c['status'] not in UNSIGNED)]))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else 'v4mH50Sz9sUdkssqcd2L'))
