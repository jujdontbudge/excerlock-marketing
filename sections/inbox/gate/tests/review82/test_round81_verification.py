"""Run round 81's reproductions and inherited verification unchanged."""
from gate.tests.review81 import test_round81 as previous
from gate.tests.review81 import test_round80_verification as older


class Round81Verification(previous.DurableIdentityRestrictions):
    pass


class Round80Verification(older.Round80Verification):
    pass


class Round79Verification(older.Round79Verification):
    pass
