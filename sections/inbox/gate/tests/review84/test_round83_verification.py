"""Unchanged round-83 assertions plus its inherited round-82/81/80/79 checks."""
from gate.tests.review3 import support  # installs forbidden HTTP before Contacts imports
from gate.tests.review83 import test_round83 as previous
from gate.tests.review83 import test_round82_verification as older


class Round83Verification(previous.LinkedAccountDelivery):
    pass


class Round82Verification(older.Round82Verification):
    pass


class Round81Verification(older.Round81Verification):
    pass


class Round80Verification(older.Round80Verification):
    pass


class Round79Verification(older.Round79Verification):
    pass
