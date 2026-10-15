"""Unchanged round-56 reproductions and controls, against the current gate."""
# Install the existing offline transport fakes before importing that round.
from gate.tests.review3 import support as _offline
from gate.tests.review56 import test_round56 as original


class Round56Verification(original.Review56):
    pass
