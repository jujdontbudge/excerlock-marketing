"""Run every supplied round-79 finding and control unchanged."""
from gate.tests.review3 import support  # installs the existing forbidden-network requests adapter
from gate.tests.review79 import test_round79 as previous


class Round79Verification(previous.UnreadableLinkedAccount):
    pass
