import pytest
from datetime import datetime
from logalyzer.aggregator import LogAggregator
from logalyzer.models import LogEntry

def test_aggregator_counts():
    agg = LogAggregator()
    agg.add(LogEntry(level="INFO", ip="1.2.3.4", status=200))
    agg.add(LogEntry(level="ERROR", ip="1.2.3.4", status=500))
    agg.add(LogEntry(level="INFO", ip="5.6.7.8", status=200))

    summary = agg.get_summary(top_n=2)
    assert summary["total_count"] == 3
    assert summary["levels"]["INFO"] == 2
    assert summary["levels"]["ERROR"] == 1
    assert summary["top_2_ips"]["1.2.3.4"] == 2
    assert summary["top_2_errors"]["500"] == 1
    assert summary["error_rate"] == 1/3

def test_aggregator_latency():
    agg = LogAggregator()
    agg.add(LogEntry(latency=0.1))
    agg.add(LogEntry(latency=0.5))
    agg.add(LogEntry(latency=0.3))

    summary = agg.get_summary()
    stats = summary["latency_stats"]
    assert stats["min"] == 0.1
    assert stats["max"] == 0.5
    assert stats["avg"] == pytest.approx(0.3)
    assert stats["count"] == 3
    assert "p95" in stats

def test_aggregator_timeline():
    agg = LogAggregator()
    t1 = datetime(2023, 1, 1, 10, 30)
    t2 = datetime(2023, 1, 1, 10, 45)
    t3 = datetime(2023, 1, 1, 11, 00)

    agg.add(LogEntry(timestamp=t1), timeline_by="hour")
    agg.add(LogEntry(timestamp=t2), timeline_by="hour")
    agg.add(LogEntry(timestamp=t3), timeline_by="hour")

    summary = agg.get_summary()
    timeline = summary["timeline"]
    assert timeline["2023-01-01 10:00"] == 2
    assert timeline["2023-01-01 11:00"] == 1
