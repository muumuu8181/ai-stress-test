import re
from datetime import datetime
from typing import Callable, Optional, List
from .models import LogEntry

FilterFunc = Callable[[LogEntry], bool]

class LogFilter:
    def __init__(self, filters: Optional[List[FilterFunc]] = None):
        self.filters = filters or []
    def add(self, filter_func: FilterFunc):
        self.filters.append(filter_func)
    def __call__(self, entry: LogEntry) -> bool:
        for f in self.filters:
            if not f(entry): return False
        return True

def level_filter(level: str) -> FilterFunc:
    def filter_func(entry: LogEntry) -> bool:
        if not entry.level: return False
        return entry.level.upper() == level.upper()
    return filter_func

def keyword_filter(keyword: str) -> FilterFunc:
    def filter_func(entry: LogEntry) -> bool:
        return keyword in entry.raw
    return filter_func

def regex_filter(pattern: str) -> FilterFunc:
    regex = re.compile(pattern)
    def filter_func(entry: LogEntry) -> bool:
        return bool(regex.search(entry.raw))
    return filter_func

def time_range_filter(start: Optional[datetime] = None, end: Optional[datetime] = None) -> FilterFunc:
    def filter_func(entry: LogEntry) -> bool:
        if not entry.timestamp or not isinstance(entry.timestamp, datetime): return False
        if start and entry.timestamp < start: return False
        if end and entry.timestamp > end: return False
        return True
    return filter_func
