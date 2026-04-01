import pytest
from datetime import datetime
from logalyzer.models import LogEntry

def test_log_entry_init():
    entry = LogEntry(
        timestamp=datetime(2023, 1, 1, 12, 0, 0),
        level="INFO",
        message="Test message",
        raw="raw info",
        ip="127.0.0.1",
        status=200,
        latency=0.05
    )
    assert entry.level == "INFO"
    assert entry.status == 200
    assert entry.latency == 0.05

def test_log_entry_get():
    entry = LogEntry(message="Main", metadata={"foo": "bar", "status": 500})
    # Should get from attribute
    assert entry.get("message") == "Main"
    # Should get from metadata
    assert entry.get("foo") == "bar"
    # Metadata fallback for existing but None attribute?
    # Current implementation check hasattr(self, key) and key != "metadata": val = getattr(self, key); if val is not None: return val
    # If attribute exists and is None, it falls back to metadata
    entry.status = None
    assert entry.get("status") == 500
    # Non-existent
    assert entry.get("non_existent") is None
