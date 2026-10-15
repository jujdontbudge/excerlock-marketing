"""Unchanged round-82 assertions and their inherited verification."""
from gate.tests.review82 import test_round82 as previous
from gate.tests.review82 import test_round81_verification as older


class Round82Verification(previous.PersonOnceDelivery):
    pass


class Round81Verification(older.Round81Verification):
    pass


class Round80Verification(older.Round80Verification):
    pass


class Round79Verification(older.Round79Verification):
    pass
