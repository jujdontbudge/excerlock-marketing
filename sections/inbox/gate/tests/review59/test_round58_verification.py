"""Re-run round 58's ten current regressions and controls, unchanged."""
from gate.tests.review58 import test_round58 as original


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromTestCase(original.Round58)
