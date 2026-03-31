from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any
from datetime import datetime

class JobStatus(Enum):
    """Enumeration of possible job statuses."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"

class ScheduleType(Enum):
    """Enumeration of supported schedule types."""
    CRON = "cron"
    INTERVAL = "interval"
    ONE_SHOT = "one_shot"

@dataclass
class JobHistory:
    """Record of a job execution."""
    job_id: str
    run_id: str
    status: JobStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    return_value: Any = None
