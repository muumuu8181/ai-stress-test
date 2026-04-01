from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime
from .models import LogEntry

class AnomalyDetector:
    def __init__(self, spike_threshold: float = 2.0, latency_threshold: float = 1.5):
        self.spike_threshold = spike_threshold
        self.latency_threshold = latency_threshold

    def detect_spikes(self, timeline: Dict[str, int]) -> List[Dict[str, Any]]:
        if not timeline: return []
        counts = list(timeline.values())
        avg_count = sum(counts) / len(counts)
        anomalies = []
        for time_key, count in sorted(timeline.items()):
            if count > avg_count * self.spike_threshold:
                anomalies.append({"type": "spike", "timestamp": time_key, "count": count, "avg": avg_count, "factor": count / avg_count if avg_count > 0 else 0})
        return anomalies

    def detect_latency_spikes(self, entries: List[LogEntry], timeline_by: str = "minute") -> List[Dict[str, Any]]:
        buckets = defaultdict(list)
        for entry in entries:
            if entry.latency is not None and entry.timestamp and isinstance(entry.timestamp, datetime):
                key = entry.timestamp.strftime("%Y-%m-%d %H:%M") if timeline_by == "minute" else entry.timestamp.strftime("%Y-%m-%d %H")
                buckets[key].append(entry.latency)
        if not buckets: return []
        all_lats = [l for b in buckets.values() for l in b]
        if not all_lats: return []
        global_avg = sum(all_lats) / len(all_lats)
        anomalies = []
        for time_key, lats in sorted(buckets.items()):
            bucket_avg = sum(lats) / len(lats)
            if bucket_avg > global_avg * self.latency_threshold:
                anomalies.append({"type": "latency_increase", "timestamp": time_key, "avg_latency": bucket_avg, "global_avg": global_avg, "factor": bucket_avg / global_avg if global_avg > 0 else 0})
        return anomalies
