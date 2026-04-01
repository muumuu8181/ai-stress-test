import json
import re
from typing import List, Dict, Any, Optional
from .models import ProfilerResult, FunctionStats


class StatsFormatter:
    """Formatter for profiling results."""

    @staticmethod
    def filter_stats(stats_dict: Dict[str, FunctionStats],
                     pattern: Optional[str] = None) -> List[FunctionStats]:
        """Filter stats by name using regex."""
        stats = list(stats_dict.values())
        if pattern:
            regex = re.compile(pattern)
            stats = [s for s in stats if regex.search(s.name) or regex.search(s.full_name)]
        return stats

    @staticmethod
    def sort_stats(stats: List[FunctionStats],
                   sort_by: str = "total_time",
                   reverse: bool = True) -> List[FunctionStats]:
        """Sort stats by a given attribute."""
        valid_sort_keys = ["total_time", "self_time", "call_count", "memory_usage", "name"]
        if sort_by not in valid_sort_keys:
            sort_by = "total_time"

        return sorted(stats, key=lambda x: getattr(x, sort_by), reverse=reverse)

    @classmethod
    def to_table(cls, result: ProfilerResult,
                 sort_by: str = "total_time",
                 filter_pattern: Optional[str] = None) -> str:
        """Format results as a plain text table."""
        stats = cls.filter_stats(result.function_stats, filter_pattern)
        stats = cls.sort_stats(stats, sort_by)

        header = f"{'Function':<50} | {'Calls':>8} | {'Total (s)':>10} | {'Self (s)':>10} | {'Mem (B)':>10}"
        separator = "-" * len(header)
        lines = [header, separator]

        for s in stats:
            # Truncate long names
            name = s.full_name if len(s.full_name) <= 50 else "..." + s.full_name[-47:]
            line = f"{name:<50} | {s.call_count:>8} | {s.total_time:>10.6f} | {s.self_time:>10.6f} | {s.memory_usage:>10}"
            lines.append(line)

        return "\n".join(lines)

    @classmethod
    def to_json(cls, result: ProfilerResult,
                filter_pattern: Optional[str] = None) -> str:
        """Format results as JSON."""
        stats = cls.filter_stats(result.function_stats, filter_pattern)
        data = {
            "functions": [
                {
                    "name": s.name,
                    "full_name": s.full_name,
                    "file": s.file_name,
                    "line": s.line_number,
                    "calls": s.call_count,
                    "total_time": s.total_time,
                    "self_time": s.self_time,
                    "memory_usage": s.memory_usage
                } for s in stats
            ],
            "call_graph": result.call_graph
        }
        return json.dumps(data, indent=2)

    @classmethod
    def to_flamegraph(cls, result: ProfilerResult) -> str:
        """Format results as a text-based flame graph (folded stack format).

        Uses 'self time' for each entry in the stack trace to avoid double-counting
        when processed by standard flame graph tools.
        """
        lines = []

        def traverse(node: Dict, prefix: str):
            # Use full_name for uniqueness in the stack representation
            stack = f"{prefix};{node['full_name']}" if prefix else node['full_name']

            duration_total = node.get("duration", 0)
            duration_children = sum(c.get("duration", 0) for c in node.get("children", []))
            # Self-time for this node in the context of the call graph
            duration_self = max(0, duration_total - duration_children)

            # duration is in seconds, use microseconds for integer representation
            duration_us = int(duration_self * 1_000_000)
            if duration_us > 0:
                lines.append(f"{stack} {duration_us}")

            for child in node.get("children", []):
                traverse(child, stack)

        for root in result.call_graph:
            traverse(root, "")

        return "\n".join(lines)
