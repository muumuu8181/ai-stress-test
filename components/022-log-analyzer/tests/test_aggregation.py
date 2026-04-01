import pytest
from datetime import datetime
from logalyzer.aggregator import LogAggregator
from logalyzer.models import LogEntry

def test_aggregator():
    agg = LogAggregator()
    agg.add(LogEntry(level="INFO", status=200, latency=0.1))
    summary = agg.get_summary()
    assert summary["total_count"] == 1
    assert summary["latency_stats"]["avg"] == 0.1
