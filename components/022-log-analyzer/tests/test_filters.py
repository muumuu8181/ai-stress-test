import pytest
from datetime import datetime
from logalyzer.filters import (
    LogFilter,
    level_filter,
    keyword_filter,
    regex_filter,
    time_range_filter
)
from logalyzer.models import LogEntry

def test_level_filter():
    f = level_filter("ERROR")
    entry_error = LogEntry(level="ERROR", raw="ERROR: something happened")
    entry_info = LogEntry(level="INFO", raw="INFO: all good")

    assert f(entry_error) is True
    assert f(entry_info) is False

def test_keyword_filter():
    f = keyword_filter("failed")
    entry1 = LogEntry(raw="Login failed for user")
    entry2 = LogEntry(raw="Login success for user")

    assert f(entry1) is True
    assert f(entry2) is False

def test_regex_filter():
    f = regex_filter(r"User \d+ logged in")
    entry1 = LogEntry(raw="User 123 logged in")
    entry2 = LogEntry(raw="User Alice logged in")

    assert f(entry1) is True
    assert f(entry2) is False

def test_time_range_filter():
    start = datetime(2023, 1, 1, 10, 0, 0)
    end = datetime(2023, 1, 1, 12, 0, 0)
    f = time_range_filter(start, end)

    entry_in = LogEntry(timestamp=datetime(2023, 1, 1, 11, 0, 0))
    entry_out = LogEntry(timestamp=datetime(2023, 1, 1, 13, 0, 0))
    entry_no_ts = LogEntry(timestamp=None)

    assert f(entry_in) is True
    assert f(entry_out) is False
    assert f(entry_no_ts) is False

def test_combined_filters():
    filters = LogFilter()
    filters.add(level_filter("ERROR"))
    filters.add(keyword_filter("critical"))

    entry1 = LogEntry(level="ERROR", raw="ERROR: critical failure")
    entry2 = LogEntry(level="ERROR", raw="ERROR: minor issue")
    entry3 = LogEntry(level="INFO", raw="INFO: critical notice")

    assert filters(entry1) is True
    assert filters(entry2) is False
    assert filters(entry3) is False
