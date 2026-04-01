import pytest
from datetime import datetime
from logalyzer.analysis import AnomalyDetector
from logalyzer.models import LogEntry

def test_detect_spikes():
    d = AnomalyDetector(spike_threshold=1.5)
    timeline = {"10:00": 10, "10:01": 40}
    assert len(d.detect_spikes(timeline)) == 1

def test_p1_timestamp_guard():
    d = AnomalyDetector()
    assert d.detect_latency_spikes([LogEntry(timestamp="string", latency=1.0)]) == []
