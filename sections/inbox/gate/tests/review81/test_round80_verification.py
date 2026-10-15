"""Run all round-80 reproductions and controls against this snapshot."""
from gate.tests.review80 import test_round80 as previous
from gate.tests.review80 import test_round79_verification as older


class Round80Verification(previous.RestrictionSurvivesHandleRemoval):
    pass


class Round79Verification(older.Round79Verification):
    pass
