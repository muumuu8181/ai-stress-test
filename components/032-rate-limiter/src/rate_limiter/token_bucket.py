import threading
import time
from .base import RateLimiter


class TokenBucketRateLimiter(RateLimiter):
    """
    Token Bucket Algorithm implementation for rate limiting.

    Attributes:
        capacity (float): Maximum number of tokens the bucket can hold.
        refill_rate (float): Number of tokens added to the bucket per second.
        tokens (float): Current number of tokens in the bucket.
        last_refill_time (float): The last time the bucket was refilled.
    """

    def __init__(self, capacity: float, refill_rate: float):
        """
        Initializes the TokenBucketRateLimiter.

        Args:
            capacity (float): Maximum number of tokens the bucket can hold.
            refill_rate (float): Number of tokens added to the bucket per second.

        Raises:
            ValueError: If capacity or refill_rate is negative.
        """
        if capacity < 0:
            raise ValueError("capacity must be non-negative")
        if refill_rate < 0:
            raise ValueError("refill_rate must be non-negative")

        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill_time = time.monotonic()
        self._lock = threading.Lock()

    def allow_request(self) -> bool:
        """
        Check if a request is allowed by the token bucket.

        Returns:
            bool: True if a token was available and consumed, False otherwise.
        """
        with self._lock:
            self._refill()
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False

    def _refill(self) -> None:
        """
        Refill the bucket with tokens based on the time elapsed since the last refill.
        """
        now = time.monotonic()
        elapsed = now - self.last_refill_time
        added_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + added_tokens)
        self.last_refill_time = now
