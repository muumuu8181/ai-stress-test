import re
from datetime import datetime
from typing import Callable, Optional, List
from .models import LogEntry

FilterFunc = Callable[[LogEntry], bool]

class LogFilter:
    """
    Combines multiple filter functions to decide if a log entry should be included.
    """
    def __init__(self, filters: Optional[List[FilterFunc]] = None):
        """Initializes the log filter with an optional list of filter functions."""
        self.filters = filters or []

    def add(self, filter_func: FilterFunc):
        """Adds a filter function to the collection."""
        self.filters.append(filter_func)

    def __call__(self, entry: LogEntry) -> bool:
        """
        Applies all filters to a log entry.

        Args:
            entry: The LogEntry to check.

        Returns:
            True if all filters pass, otherwise False.
        """
        for f in self.filters:
            if not f(entry):
                return False
        return True

def level_filter(level: str) -> FilterFunc:
    """
    Creates a filter that matches the log level.

    Args:
        level: The log level to match (case-insensitive).

    Returns:
        A filter function.
    """
    def filter_func(entry: LogEntry) -> bool:
        if not entry.level:
            return False
        return entry.level.upper() == level.upper()
    return filter_func

def keyword_filter(keyword: str) -> FilterFunc:
    """
    Creates a filter that matches a keyword in the raw log.

    Args:
        keyword: The string to search for.

    Returns:
        A filter function.
    """
    def filter_func(entry: LogEntry) -> bool:
        return keyword in entry.raw
    return filter_func

def regex_filter(pattern: str) -> FilterFunc:
    """
    Creates a filter that matches a regex in the raw log.

    Args:
        pattern: The regex pattern to match.

    Returns:
        A filter function.
    """
    regex = re.compile(pattern)
    def filter_func(entry: LogEntry) -> bool:
        return bool(regex.search(entry.raw))
    return filter_func

def time_range_filter(start: Optional[datetime] = None, end: Optional[datetime] = None) -> FilterFunc:
    """
    Creates a filter that checks if the log entry is within a time range.

    Args:
        start: The beginning of the time range (inclusive).
        end: The end of the time range (inclusive).

    Returns:
        A filter function.
    """
    def filter_func(entry: LogEntry) -> bool:
        if not entry.timestamp or not isinstance(entry.timestamp, datetime):
            return False
        if start and entry.timestamp < start:
            return False
        if end and entry.timestamp > end:
            return False
        return True
    return filter_func
