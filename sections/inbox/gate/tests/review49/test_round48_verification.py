"""Run the unmodified round-48 regressions against this snapshot."""
from gate.tests.review48 import test_review48 as round48


class Round48Verification(round48.Review48):
    pass
