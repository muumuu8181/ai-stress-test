import datetime
from typing import List, Set, Optional

class CronParser:
    """A simple cron parser that supports basic cron expressions."""

    def __init__(self, cron_expression: str):
        """
        Initialize the CronParser.

        Args:
            cron_expression: A string representing a cron expression (minute hour day-of-month month day-of-week).
                             Supports '*', fixed values, ranges (e.g., 1-5), and intervals (e.g., */15).
        """
        self.expression = cron_expression
        self.parts = cron_expression.split()
        if len(self.parts) != 5:
            raise ValueError("Cron expression must have 5 parts (minute hour day month weekday)")

        self.minutes = self._parse_part(self.parts[0], 0, 59)
        self.hours = self._parse_part(self.parts[1], 0, 23)
        self.days = self._parse_part(self.parts[2], 1, 31)
        self.months = self._parse_part(self.parts[3], 1, 12)

        # Standard Cron: 0-6 (Sun-Sat), sometimes 7 is also Sunday.
        cron_weekdays = self._parse_part(self.parts[4], 0, 7)
        self.weekdays = set()
        for wd in cron_weekdays:
            if wd == 0 or wd == 7:
                self.weekdays.add(6)  # Sunday in Python's weekday()
            else:
                self.weekdays.add(wd - 1)  # Monday(1)->0, ..., Saturday(6)->5

        # Check for empty sets to avoid infinite loops in get_next_occurrence
        if not all([self.minutes, self.hours, self.days, self.months, self.weekdays]):
            raise ValueError("Cron expression resulted in an empty set for one or more fields")

        # Standard Vixie Cron behavior: if both DOM and DOW are restricted, it's an OR logic.
        # Restricted means not '*'.
        self.dom_restricted = self.parts[2] != "*"
        self.dow_restricted = self.parts[4] != "*"

    def _parse_part(self, part: str, min_val: int, max_val: int) -> Set[int]:
        """Parse a single part of a cron expression."""
        if part == "*":
            return set(range(min_val, max_val + 1))

        values: Set[int] = set()
        for segment in part.split(","):
            if "/" in segment:
                base, step_str = segment.split("/")
                step = int(step_str)
                if step <= 0:
                    raise ValueError(f"Step value {step} must be positive")
                if base == "*":
                    values.update(range(min_val, max_val + 1, step))
                elif "-" in base:
                    start_str, end_str = base.split("-")
                    start, end = int(start_str), int(end_str)
                    if start > end:
                        raise ValueError(f"Range start {start} is greater than end {end}")
                    values.update(range(start, end + 1, step))
                else:
                    values.update(range(int(base), max_val + 1, step))
            elif "-" in segment:
                start_str, end_str = segment.split("-")
                start, end = int(start_str), int(end_str)
                if start > end:
                    raise ValueError(f"Range start {start} is greater than end {end}")
                values.update(range(start, end + 1))
            else:
                values.add(int(segment))

        # Validate values
        for v in values:
            if not (min_val <= v <= max_val):
                raise ValueError(f"Value {v} out of range ({min_val}-{max_val})")

        return values

    def get_next_occurrence(self, start_time: datetime.datetime) -> datetime.datetime:
        """
        Calculate the next occurrence of the cron schedule after the given start time.

        Args:
            start_time: The time from which to start searching for the next occurrence.

        Returns:
            The datetime of the next occurrence.
        """
        # Start looking from the next minute
        next_run = start_time.replace(second=0, microsecond=0) + datetime.timedelta(minutes=1)

        while True:
            if next_run.month not in self.months:
                # Go to next month
                if next_run.month == 12:
                    next_run = next_run.replace(year=next_run.year + 1, month=1, day=1, hour=0, minute=0)
                else:
                    next_run = next_run.replace(month=next_run.month + 1, day=1, hour=0, minute=0)
                continue

            # Standard Cron: if both DOM and DOW are restricted, it's OR.
            # Otherwise, it's AND.
            if self.dom_restricted and self.dow_restricted:
                if next_run.day not in self.days and next_run.weekday() not in self.weekdays:
                    next_run += datetime.timedelta(days=1)
                    next_run = next_run.replace(hour=0, minute=0)
                    continue
            else:
                if next_run.day not in self.days or next_run.weekday() not in self.weekdays:
                    next_run += datetime.timedelta(days=1)
                    next_run = next_run.replace(hour=0, minute=0)
                    continue

            if next_run.hour not in self.hours:
                next_run += datetime.timedelta(hours=1)
                next_run = next_run.replace(minute=0)
                continue

            if next_run.minute not in self.minutes:
                next_run += datetime.timedelta(minutes=1)
                continue

            return next_run
