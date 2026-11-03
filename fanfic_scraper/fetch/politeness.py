import random
import time


class Politeness:
    def __init__(self, min_delay=5.0, max_delay=10.0, sleep_fn=time.sleep,
                 clock_fn=time.monotonic, rand_fn=random.uniform):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.sleep_fn = sleep_fn
        self.clock_fn = clock_fn
        self.rand_fn = rand_fn
        self._last_request_at = {}

    def wait_for(self, host: str, min_delay=None, max_delay=None) -> float:
        lo = self.min_delay if min_delay is None else min_delay
        hi = self.max_delay if max_delay is None else max_delay
        target_delay = self.rand_fn(lo, hi)
        last = self._last_request_at.get(host)
        slept = 0.0
        if last is not None:
            remaining = target_delay - (self.clock_fn() - last)
            if remaining > 0:
                self.sleep_fn(remaining)
                slept = remaining
        self._last_request_at[host] = self.clock_fn()
        return slept
