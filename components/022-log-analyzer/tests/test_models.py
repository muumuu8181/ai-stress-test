import pytest
from datetime import datetime
from logalyzer.models import LogEntry

def test_log_entry_init():
    entry = LogEntry(timestamp=datetime(2023, 1, 1), level="INFO", status=200, latency=0.05)
    assert entry.level == "INFO"
    assert entry.status == 200

def test_log_entry_get():
    entry = LogEntry(message="Main", metadata={"foo": "bar"})
    assert entry.get("message") == "Main"
    assert entry.get("foo") == "bar"
