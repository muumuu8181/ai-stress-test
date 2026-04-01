from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union
from datetime import datetime

@dataclass
class LogEntry:
    """
    Represents a single structured log entry.
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
        if hasattr(self, key) and key != "metadata":
            val = getattr(self, key)
            if val is not None:
                return val
        return self.metadata.get(key)
