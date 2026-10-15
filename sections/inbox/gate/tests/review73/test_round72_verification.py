"""Run round 72's fourteen counterexamples and controls without adapting them."""
from gate.tests.review72 import test_round72 as prior


class InviteVerification(prior.ObservedInviteTransition):
    pass


class SigningVerification(prior.ObservedSigningTransition):
    pass
