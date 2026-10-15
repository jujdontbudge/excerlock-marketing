"""Run all supplied round-75 assertions unchanged against this snapshot."""
from gate.tests.review75 import test_round75 as prior


class Round75InviteVerification(prior.RecycledRepostInvite):
    pass


class Round75GapVerification(prior.CompanyDeliveryActivity):
    pass
