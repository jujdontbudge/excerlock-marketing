from pathlib import Path

# The inbox's automatic-reply switch (sections/inbox/INBOX_AUTO) is the captain's choice and is OFF by default. The
# adversarial suites were written against per-type modes, so they run with it ON; test_inbox_switch.py checks the
# default (drafts) explicitly.
try:
    import propose as _propose
    _propose.INBOX_AUTO = Path(__file__)   # an existing path = switch on, for these suites only
except Exception:
    pass

# The suites run against a frozen copy of the message types (fixtures/messages), so changing or un-approving a real
# message's wording (approved: pending while the captain reviews it) can't make unrelated gate tests fail.
from gate import policy as _policy   # noqa: E402
_policy.MESSAGES = Path(__file__).resolve().parent / 'fixtures' / 'messages'
_policy.load.__defaults__ = (_policy.MESSAGES,)
