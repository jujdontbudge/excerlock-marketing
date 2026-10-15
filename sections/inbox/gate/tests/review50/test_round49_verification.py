"""Run the original round-49 counterexamples unchanged against this snapshot."""
from gate.tests.review49.test_round49 import Review49


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromTestCase(Review49)
