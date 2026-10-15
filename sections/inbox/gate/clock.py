"""How old evidence is, counting time the computer was asleep (review DA01).

time.monotonic() on macOS is mach_absolute_time(), which stops while the Mac sleeps, so a check read before a sleep
would look seconds old after waking. Age is therefore the largest of three clocks: monotonic (immune to the wall clock
being set back, X04), the wall clock (keeps running through sleep) and the OS clock that counts sleep
(CLOCK_BOOTTIME on Linux, CLOCK_MONOTONIC on macOS, which is mach_continuous_time).
"""
import time
from datetime import datetime, timezone


def _continuous():
    for name in ('CLOCK_BOOTTIME', 'CLOCK_MONOTONIC'):
        clk = getattr(time, name, None)
        if clk is not None:
            try:
                return time.clock_gettime(clk)
            except OSError:
                pass
    return time.monotonic()


class Since:
    """Started when the first piece of evidence is about to be read; .age() is how old that evidence is now."""
    def __init__(self, wall=None):
        self.wall = wall or (lambda: datetime.now(timezone.utc))
        self.m, self.w, self.c = time.monotonic(), self.wall(), _continuous()

    def age(self):
        return max(time.monotonic() - self.m, (self.wall() - self.w).total_seconds(), _continuous() - self.c)
