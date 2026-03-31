import uuid
import datetime
import time
import threading
from typing import Callable, Any, List, Optional, Dict
from .models import JobStatus, ScheduleType, JobHistory
from .cron import CronParser

class Job:
    """Represents a job to be executed by the scheduler."""

    def __init__(
        self,
        func: Callable[..., Any],
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
        job_id: Optional[str] = None,
        priority: int = 0,
        dependencies: Optional[List[str]] = None,
        schedule_type: ScheduleType = ScheduleType.ONE_SHOT,
        schedule_value: Optional[Any] = None,
        timeout: Optional[float] = None,
        max_retries: int = 0,
        retry_delay: float = 1.0,
        retry_backoff: float = 2.0,
    ):
        """
        Initialize a Job.

        Args:
            func: The function to execute.
            args: Positional arguments for the function.
            kwargs: Keyword arguments for the function.
            job_id: Unique identifier for the job.
            priority: Priority of the job (higher value means higher priority).
            dependencies: List of job IDs that must complete successfully before this job.
            schedule_type: The type of schedule.
            schedule_value: Value for the schedule (e.g., cron string, interval in seconds).
            timeout: Maximum execution time in seconds.
            max_retries: Maximum number of retry attempts.
            retry_delay: Initial delay between retries in seconds.
            retry_backoff: Multiplier for exponential backoff.
        """
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.job_id = job_id or str(uuid.uuid4())
        self.priority = priority
        self.dependencies = dependencies or []
        self.schedule_type = schedule_type
        self.schedule_value = schedule_value
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff

        self.status = JobStatus.PENDING
        self.last_run_id: Optional[str] = None
        self.next_run_time: Optional[datetime.datetime] = None
        self.retries_count = 0
        self.cron_parser: Optional[CronParser] = None

        if self.schedule_type == ScheduleType.CRON:
            if not isinstance(self.schedule_value, str):
                raise ValueError("Cron schedule value must be a string")
            self.cron_parser = CronParser(self.schedule_value)

        self._lock = threading.Lock()
        self.update_next_run_time(datetime.datetime.now())

    def update_next_run_time(self, now: datetime.datetime) -> None:
        """Calculate and update the next run time based on the schedule."""
        with self._lock:
            if self.schedule_type == ScheduleType.ONE_SHOT:
                if (self.status == JobStatus.PENDING or self.status == JobStatus.RETRYING) and self.next_run_time is None:
                    self.next_run_time = now
                else:
                    self.next_run_time = None
            elif self.schedule_type == ScheduleType.INTERVAL:
                if not isinstance(self.schedule_value, (int, float)):
                    raise ValueError("Interval schedule value must be a number")
                if self.next_run_time is None:
                    self.next_run_time = now
                else:
                    # Update next run time to be in the future relative to now if it has passed
                    if self.next_run_time <= now:
                        self.next_run_time += datetime.timedelta(seconds=self.schedule_value)
                    while self.next_run_time <= now:
                         self.next_run_time += datetime.timedelta(seconds=self.schedule_value)
            elif self.schedule_type == ScheduleType.CRON:
                if self.cron_parser:
                    self.next_run_time = self.cron_parser.get_next_occurrence(now)

    def should_run(self, now: datetime.datetime) -> bool:
        """Check if the job should be executed now."""
        with self._lock:
            if self.status not in [JobStatus.PENDING, JobStatus.RETRYING]:
                return False
            if self.next_run_time is None:
                return False
            return now >= self.next_run_time

    def get_retry_delay(self) -> float:
        """Calculate the delay for the next retry attempt."""
        return self.retry_delay * (self.retry_backoff ** self.retries_count)
