from abc import ABC, abstractmethod

class RateLimiter(ABC):
    """
    Abstract base class for Rate Limiter implementations.
    """

    @abstractmethod
    def allow_request(self) -> bool:
        """
        Determine if a request should be allowed or rate limited.

        Returns:
            bool: True if the request is allowed, False otherwise.
        """
        pass
