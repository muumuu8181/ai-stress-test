from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union
from datetime import datetime

@dataclass
class LogEntry:
    """
    Represents a single structured log entry.

    Attributes:
        timestamp: The date and time of the log entry.
        level: Log level (e.g., INFO, ERROR).
        message: The main log message.
        raw: The original raw log line.
        ip: Client IP address if available.
        status: HTTP status code or similar numeric status if available.
        latency: Response time or latency in seconds/milliseconds if available.
        metadata: Additional fields extracted from the log.
    """
    timestamp: Optional[Union[datetime, str]] = None
    level: Optional[str] = None
    message: Optional[str] = None
    raw: str = ""
    ip: Optional[str] = None
    status: Optional[int] = None
    latency: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str) -> Any:
        """
        Retrieves a value from the log entry by key.
        Checks specific attributes first, then falls back to metadata.

        Args:
            key: The key to retrieve.

        Returns:
            The value associated with the key, or None if not found.
        """
        if hasattr(self, key) and key != "metadata":
            val = getattr(self, key)
            if val is not None:
                return val
        return self.metadata.get(key)
