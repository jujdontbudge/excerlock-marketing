"""Re-run every round-87 finding and control against the current implementation."""
from gate.tests.review87 import test_round87 as previous


class Round87Verification(previous.WithdrawalIdentityFreshness):
    pass
