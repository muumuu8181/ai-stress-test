from typing import Dict, Any, List, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime
from .models import LogEntry

class LogAggregator:
    """
    Aggregates log entries to provide statistics and reports.
    """
    def __init__(self):
        """Initializes the aggregator with empty statistics."""
        self.count = 0
        self.levels = Counter()
        self.ips = Counter()
        self.errors = Counter()
        self.paths = Counter()
        self.latencies: List[float] = []
        self.timeline = defaultdict(int)

    def add(self, entry: LogEntry, timeline_by: str = "hour"):
        """
        Adds a single log entry to the aggregate statistics.

        Args:
            entry: The LogEntry to add.
            timeline_by: Time granularity for the timeline ('minute', 'hour', 'day').
        """
        self.count += 1

        # Log Levels
        if entry.level:
            self.levels[entry.level.upper()] += 1

        # IP Tracking
        if entry.ip:
            self.ips[entry.ip] += 1

        # Error Tracking
        if entry.status and entry.status >= 400:
            self.errors[str(entry.status)] += 1
        elif entry.level and entry.level.upper() in ["ERROR", "CRITICAL", "FATAL", "SEVERE"]:
            self.errors[entry.level.upper()] += 1

        # Path Tracking (if available in metadata)
        path = entry.get("path")
        if path:
            self.paths[path] += 1

        # Latency/Response Time
        if entry.latency is not None:
            self.latencies.append(entry.latency)

        # Timeline
        if entry.timestamp and isinstance(entry.timestamp, datetime):
            if timeline_by == "minute":
                key = entry.timestamp.strftime("%Y-%m-%d %H:%M")
            elif timeline_by == "hour":
                key = entry.timestamp.strftime("%Y-%m-%d %H:00")
            elif timeline_by == "day":
                key = entry.timestamp.strftime("%Y-%m-%d")
            else:
                key = entry.timestamp.strftime("%Y-%m-%d %H:00")
            self.timeline[key] += 1

    def get_summary(self, top_n: int = 10) -> Dict[str, Any]:
        """
        Computes and returns a summary of the aggregated data.

        Args:
            top_n: Number of top elements to return for IPs, errors, etc.

        Returns:
            A dictionary containing various statistics.
        """
        summary = {
            "total_count": self.count,
            "levels": dict(self.levels),
            f"top_{top_n}_ips": dict(self.ips.most_common(top_n)),
            f"top_{top_n}_errors": dict(self.errors.most_common(top_n)),
            f"top_{top_n}_paths": dict(self.paths.most_common(top_n)),
            "timeline": dict(sorted(self.timeline.items()))
        }

        if self.latencies:
            summary["latency_stats"] = {
                "min": min(self.latencies),
                "max": max(self.latencies),
                "avg": sum(self.latencies) / len(self.latencies),
                "count": len(self.latencies)
            }
            # Add simple percentile if needed (p95)
            sorted_latencies = sorted(self.latencies)
            idx_95 = int(len(sorted_latencies) * 0.95)
            summary["latency_stats"]["p95"] = sorted_latencies[idx_95]

        # Error Rate
        total_errors = sum(self.errors.values())
        summary["error_rate"] = (total_errors / self.count) if self.count > 0 else 0

        return summary
