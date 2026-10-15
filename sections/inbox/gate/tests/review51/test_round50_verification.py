"""Run the original round-50 counterexamples unchanged."""
from gate.tests.review3 import support  # install the existing network-forbidden HTTP fake first
from gate.tests.review50.test_round50 import Review50


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromTestCase(Review50)
