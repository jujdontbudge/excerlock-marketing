"""Run all eight round-52 regressions against this snapshot, offline."""
from gate.tests.review3 import support  # installs the network-forbidden requests fake
from gate.tests.review52 import test_round52


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromTestCase(test_round52.Review52)
