"""Use the supplied offline domain fixtures; no network or real subprocess effects."""
from gate.tests.review3.support import (Case, NOW, Live, Sender, conv, invite, msg,
                                       contacts, flow, grant, handles, policy, propose, withdraw)
from gate.tests.review3.test_propose_grant import Proposals


class InboxCase(Case):
    run_inbox = Proposals.run_inbox
