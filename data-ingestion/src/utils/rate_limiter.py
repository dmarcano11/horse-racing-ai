"""Rate limiter to respect API limits (2 requests/second)."""
import time
from collections import deque
from typing import Deque
from threading import Lock


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, max_requests: int = 2, period: float = 1.0):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in period
            period: Time period in seconds
        """
        self.max_requests = max_requests
        self.period = period
        self.requests: Deque[float] = deque()
        self.lock = Lock()

    def wait_if_needed(self) -> float:
        """
        Wait if necessary to respect rate limit.

        Returns:
            Time waited in seconds
        """
        with self.lock:
            now = time.time()

            # Remove requests outside the current period
            while self.requests and self.requests[0] <= now - self.period:
                self.requests.popleft()

            # If at limit, wait until oldest request expires
            if len(self.requests) >= self.max_requests:
                sleep_time = self.period - (now - self.requests[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    now = time.time()
                    # Clean up again after sleep
                    while self.requests and self.requests[0] <= now - self.period:
                        self.requests.popleft()

            # Record this request
            self.requests.append(now)

            return 0.0

    def reset(self):
        """Reset rate limiter state."""
        with self.lock:
            self.requests.clear()