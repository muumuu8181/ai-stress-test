from typing import List, Dict, Any, Optional
from collections import defaultdict
from .models import LogEntry

class AnomalyDetector:
    """
    Analyzes log streams to detect anomalies like spikes or latency increases.
    """
    def __init__(self, spike_threshold: float = 3.0, latency_threshold: float = 2.0):
        """
        Initializes the detector.

        Args:
            spike_threshold: Threshold factor for spikes (e.g., 3.0 means 3x average).
            latency_threshold: Threshold factor for latency (e.g., 2.0 means 2x average).
        """
        self.spike_threshold = spike_threshold
        self.latency_threshold = latency_threshold

    def detect_spikes(self, timeline: Dict[str, int]) -> List[Dict[str, Any]]:
        """
        Detects spikes in the log entry count over time.

        Args:
            timeline: A dictionary mapping time intervals to counts.

        Returns:
            A list of detected spikes with details.
        """
        if not timeline:
            return []

        counts = list(timeline.values())
        avg_count = sum(counts) / len(counts)
        anomalies = []

        for time_key, count in sorted(timeline.items()):
            if count > avg_count * self.spike_threshold:
                anomalies.append({
                    "type": "spike",
                    "timestamp": time_key,
                    "count": count,
                    "avg": avg_count,
                    "factor": count / avg_count if avg_count > 0 else 0
                })
        return anomalies

    def detect_latency_spikes(self, entries: List[LogEntry], timeline_by: str = "minute") -> List[Dict[str, Any]]:
        """
        Detects periods with higher than average response times.

        Args:
            entries: A list of LogEntries.
            timeline_by: Time granularity for the analysis.

        Returns:
            A list of latency anomalies with details.
        """
        # Bucket latency by time
        buckets = defaultdict(list)
        for entry in entries:
            if entry.latency is not None and entry.timestamp:
                key = entry.timestamp.strftime("%Y-%m-%d %H:%M") if timeline_by == "minute" else entry.timestamp.strftime("%Y-%m-%d %H")
                buckets[key].append(entry.latency)

        if not buckets:
            return []

        # Calculate overall average
        all_latencies = [l for b in buckets.values() for l in b]
        if not all_latencies:
            return []
        global_avg = sum(all_latencies) / len(all_latencies)

        anomalies = []
        for time_key, lats in sorted(buckets.items()):
            bucket_avg = sum(lats) / len(lats)
            if bucket_avg > global_avg * self.latency_threshold:
                anomalies.append({
                    "type": "latency_increase",
                    "timestamp": time_key,
                    "avg_latency": bucket_avg,
                    "global_avg": global_avg,
                    "factor": bucket_avg / global_avg if global_avg > 0 else 0
                })
        return anomalies
