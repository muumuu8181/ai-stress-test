import pytest
from datetime import datetime
from logalyzer.analysis import AnomalyDetector
from logalyzer.models import LogEntry

def test_detect_spikes():
    detector = AnomalyDetector(spike_threshold=1.5) # Lower threshold for test
    # Average count: (10+11+9+30+10)/5 = 70/5 = 14
    # Threshold: 14 * 1.5 = 21
    timeline = {
        "10:00": 10,
        "10:01": 11,
        "10:02": 9,
        "10:03": 30, # Spike (> 21)
        "10:04": 10
    }
    spikes = detector.detect_spikes(timeline)
    assert len(spikes) == 1
    assert spikes[0]["timestamp"] == "10:03"
    assert spikes[0]["count"] == 30

def test_detect_latency_spikes():
    detector = AnomalyDetector(latency_threshold=2.0)
    t1 = datetime(2023, 1, 1, 10, 0)
    t2 = datetime(2023, 1, 1, 10, 1)

    entries = [
        LogEntry(timestamp=t1, latency=0.1),
        LogEntry(timestamp=t1, latency=0.15),
        LogEntry(timestamp=t1, latency=0.12),
        LogEntry(timestamp=t2, latency=1.5), # Latency Spike
        LogEntry(timestamp=t2, latency=1.2)
    ]

    anomalies = detector.detect_latency_spikes(entries, timeline_by="minute")
    assert len(anomalies) == 1
    assert anomalies[0]["timestamp"] == "2023-01-01 10:01"
    assert anomalies[0]["avg_latency"] == 1.35
    assert anomalies[0]["global_avg"] == pytest.approx((0.1+0.15+0.12+1.5+1.2)/5)

def test_no_anomalies():
    detector = AnomalyDetector()
    assert detector.detect_spikes({}) == []
    assert detector.detect_latency_spikes([]) == []

    timeline = {"10:00": 10, "10:01": 10}
    assert detector.detect_spikes(timeline) == []
