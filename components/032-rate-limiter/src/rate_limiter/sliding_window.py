import threading
import time
from collections import deque
from .base import RateLimiter


class SlidingWindowRateLimiter(RateLimiter):
    """
    Sliding Window Log Algorithm implementation for rate limiting.

    Attributes:
        max_requests (int): The maximum number of requests allowed within the window.
        window_seconds (float): The time window in seconds.
        requests (deque): A deque containing timestamps of recent requests.
    """

    def __init__(self, max_requests: int, window_seconds: float):
        """
        Initializes the SlidingWindowRateLimiter.

        Args:
            max_requests (int): The maximum number of requests allowed within the window.
            window_seconds (float): The time window in seconds.
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
        self._lock = threading.Lock()

    def allow_request(self) -> bool:
        """
        Check if a request is allowed by the sliding window log.

        Returns:
            bool: True if the request is within the limit, False otherwise.
        """
        with self._lock:
            now = time.time()
            self._cleanup(now)
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False

    def _cleanup(self, now: float) -> None:
        """
        Remove timestamps from the request log that are outside the current time window.

        Args:
            now (float): Current timestamp.
        """
        while self.requests and self.requests[0] <= now - self.window_seconds:
            self.requests.popleft()
