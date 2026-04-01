import pytest
from datetime import datetime
from logalyzer.filters import level_filter, time_range_filter
from logalyzer.models import LogEntry

def test_level_filter():
    f = level_filter("ERROR")
    assert f(LogEntry(level="ERROR")) is True
    assert f(LogEntry(level="INFO")) is False

def test_time_range_filter():
    start, end = datetime(2023, 1, 1, 10), datetime(2023, 1, 1, 12)
    f = time_range_filter(start, end)
    assert f(LogEntry(timestamp=datetime(2023, 1, 1, 11))) is True
    assert f(LogEntry(timestamp=datetime(2023, 1, 1, 13))) is False
