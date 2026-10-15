"""Run the original round-51 regressions unchanged, without network."""
from gate.tests.review3 import support  # install the existing network-forbidden HTTP fake
from gate.tests.review51 import test_round51


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromTestCase(test_round51.Review51)
