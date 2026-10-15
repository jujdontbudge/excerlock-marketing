"""Run all supplied round-77 assertions unchanged on the reviewed snapshot."""
from gate.tests.review77 import test_round77 as previous


class Round77Verification(previous.MediaNoticeExemption):
    pass
