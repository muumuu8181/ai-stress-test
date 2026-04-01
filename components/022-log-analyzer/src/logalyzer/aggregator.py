from typing import Dict, Any, List, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime
from .models import LogEntry

class LogAggregator:
    def __init__(self):
        self.count = 0
        self.levels = Counter()
        self.ips = Counter()
        self.errors = Counter()
        self.paths = Counter()
        self.latency_count = 0
        self.latency_sum = 0.0
        self.latency_min = float('inf')
        self.latency_max = float('-inf')
        self.latency_sample: List[float] = []
        self.max_sample_size = 10000
        self.timeline = defaultdict(int)

    def add(self, entry: LogEntry, timeline_by: str = "hour"):
        self.count += 1
        if entry.level: self.levels[entry.level.upper()] += 1
        if entry.ip: self.ips[entry.ip] += 1
        if entry.status and entry.status >= 400: self.errors[str(entry.status)] += 1
        elif entry.level and entry.level.upper() in ["ERROR", "CRITICAL", "FATAL", "SEVERE"]: self.errors[entry.level.upper()] += 1
        path = entry.get("path")
        if path: self.paths[path] += 1
        if entry.latency is not None:
            self.latency_count += 1
            self.latency_sum += entry.latency
            if entry.latency < self.latency_min: self.latency_min = entry.latency
            if entry.latency > self.latency_max: self.latency_max = entry.latency
            if len(self.latency_sample) < self.max_sample_size: self.latency_sample.append(entry.latency)
        if entry.timestamp and isinstance(entry.timestamp, datetime):
            fmt = {"minute": "%Y-%m-%d %H:%M", "hour": "%Y-%m-%d %H:00", "day": "%Y-%m-%d"}.get(timeline_by, "%Y-%m-%d %H:00")
            self.timeline[entry.timestamp.strftime(fmt)] += 1

    def get_summary(self, top_n: int = 10) -> Dict[str, Any]:
        summary = {"total_count": self.count, "levels": dict(self.levels), f"top_{top_n}_ips": dict(self.ips.most_common(top_n)), f"top_{top_n}_errors": dict(self.errors.most_common(top_n)), f"top_{top_n}_paths": dict(self.paths.most_common(top_n)), "timeline": dict(sorted(self.timeline.items()))}
        if self.latency_count > 0:
            summary["latency_stats"] = {"min": self.latency_min, "max": self.latency_max, "avg": self.latency_sum / self.latency_count, "count": self.latency_count}
            if self.latency_sample:
                sorted_latencies = sorted(self.latency_sample)
                idx_95 = int(len(sorted_latencies) * 0.95)
                summary["latency_stats"]["p95_approx"] = sorted_latencies[idx_95]
        summary["error_rate"] = (sum(self.errors.values()) / self.count) if self.count > 0 else 0
        return summary
