"""Unchanged round-84 required-behavior assertions and their controls."""
from gate.tests.review84 import test_round84


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromModule(test_round84)
