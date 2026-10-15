"""Run all ten supplied round-73 regressions and controls without further changes."""
from gate.tests.review73 import test_round73 as prior


class Round73Verification(prior.RepeatedObservation):
    pass
