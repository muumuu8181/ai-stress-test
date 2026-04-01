import sys
import argparse
import json
from typing import Optional, List, Dict, Any, Iterable
from datetime import datetime
from .parsers import (
    BaseParser,
    ApacheCombinedParser,
    NginxParser,
    JSONParser,
    CustomRegexParser
)
from .filters import (
    LogFilter,
    level_filter,
    keyword_filter,
    regex_filter,
    time_range_filter
)
from .aggregator import LogAggregator
from .analysis import AnomalyDetector
from .models import LogEntry

def get_parser(format_name: str, custom_pattern: Optional[str] = None) -> BaseParser:
    """Returns a log parser instance based on the format name."""
    if format_name == "apache":
        return ApacheCombinedParser()
    elif format_name == "nginx":
        return NginxParser()
    elif format_name == "json":
        # For JSON, we try to support ISO format by default if not specified
        return JSONParser(date_format="%Y-%m-%dT%H:%M:%S")
    elif format_name == "custom" and custom_pattern:
        return CustomRegexParser(custom_pattern)
    else:
        # Default to Apache
        return ApacheCombinedParser()

def stream_logs(file_path: str, parser: BaseParser, filters: LogFilter) -> Iterable[LogEntry]:
    """Streams log entries from a file, applying filters."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                entry = parser.parse_line(line)
                if entry and filters(entry):
                    yield entry
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

def run_analyze(args):
    """Handles the 'analyze' command."""
    parser_inst = get_parser(args.format, args.custom_pattern)
    filters = LogFilter()
    if args.level:
        filters.add(level_filter(args.level))
    if args.keyword:
        filters.add(keyword_filter(args.keyword))
    if args.regex:
        filters.add(regex_filter(args.regex))

    aggregator = LogAggregator()
    for entry in stream_logs(args.file, parser_inst, filters):
        aggregator.add(entry)

    summary = aggregator.get_summary(top_n=args.top_errors)

    if args.json:
        print(json.dumps(summary, indent=2, default=str))
    else:
        print("=== Log Analysis Report ===")
        print(f"File: {args.file}")
        print(f"Total Entries Processed: {summary['total_count']}")
        print(f"Error Rate: {summary['error_rate']:.2%}")

        print("\nLog Levels:")
        for level, count in summary['levels'].items():
            print(f"  {level}: {count}")

        print(f"\nTop {args.top_errors} IPs:")
        for ip, count in summary.get(f"top_{args.top_errors}_ips", {}).items():
            print(f"  {ip}: {count}")

        print(f"\nTop {args.top_errors} Errors:")
        for err, count in summary.get(f"top_{args.top_errors}_errors", {}).items():
            print(f"  {err}: {count}")

        if "latency_stats" in summary:
            print("\nResponse Time Statistics:")
            stats = summary["latency_stats"]
            print(f"  Min: {stats['min']:.4f}")
            print(f"  Max: {stats['max']:.4f}")
            print(f"  Avg: {stats['avg']:.4f}")
            print(f"  p95: {stats['p95']:.4f}")

def run_timeline(args):
    """Handles the 'timeline' command."""
    parser_inst = get_parser(args.format)
    filters = LogFilter()
    aggregator = LogAggregator()

    for entry in stream_logs(args.file, parser_inst, filters):
        aggregator.add(entry, timeline_by=args.by)

    summary = aggregator.get_summary()
    timeline = summary.get("timeline", {})

    if args.json:
        print(json.dumps(timeline, indent=2))
    else:
        print(f"=== Timeline (by {args.by}) ===")
        for time_key, count in timeline.items():
            print(f"{time_key}: {'#' * (count // (max(timeline.values()) // 50 + 1)) if timeline.values() else ''} ({count})")

def run_detect_anomaly(args):
    """Handles the 'detect-anomaly' command."""
    parser_inst = get_parser(args.format)
    filters = LogFilter()
    detector = AnomalyDetector()
    aggregator = LogAggregator()
    entries = []

    # For latency anomalies, we might need entries in memory or a windowed approach
    # For large files, we should probably do a two-pass or windowed.
    # Here we use the aggregator for spikes and a subset for latency if not too large.
    for entry in stream_logs(args.file, parser_inst, filters):
        aggregator.add(entry, timeline_by="minute")
        if entry.latency is not None:
            entries.append(entry)

    summary = aggregator.get_summary()
    spikes = detector.detect_spikes(summary.get("timeline", {}))
    latency_spikes = detector.detect_latency_spikes(entries)

    all_anomalies = {
        "spikes": spikes,
        "latency_anomalies": latency_spikes
    }

    if args.json:
        print(json.dumps(all_anomalies, indent=2))
    else:
        print("=== Anomaly Detection Report ===")
        if not spikes and not latency_spikes:
            print("No anomalies detected.")

        if spikes:
            print("\nTraffic Spikes Detected:")
            for spike in spikes:
                print(f"  - {spike['timestamp']}: {spike['count']} entries (Factor: {spike['factor']:.2f}x avg)")

        if latency_spikes:
            print("\nLatency Increases Detected:")
            for spike in latency_spikes:
                print(f"  - {spike['timestamp']}: Avg {spike['avg_latency']:.4f} (Factor: {spike['factor']:.2f}x global avg)")

def main():
    parser = argparse.ArgumentParser(prog="logalyzer", description="Log File Analyzer")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Analyze Command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze log file for general statistics")
    analyze_parser.add_argument("file", help="Path to the log file")
    analyze_parser.add_argument("--format", choices=["apache", "nginx", "json", "custom"], default="apache", help="Log format")
    analyze_parser.add_argument("--custom-pattern", help="Custom regex pattern (required if format is 'custom')")
    analyze_parser.add_argument("--level", help="Filter by log level")
    analyze_parser.add_argument("--keyword", help="Filter by keyword in raw log")
    analyze_parser.add_argument("--regex", help="Filter by regex in raw log")
    analyze_parser.add_argument("--top-errors", type=int, default=10, help="Number of top errors/IPs to show")
    analyze_parser.add_argument("--json", action="store_true", help="Output report in JSON format")

    # Timeline Command
    timeline_parser = subparsers.add_parser("timeline", help="Display a timeline of log events")
    timeline_parser.add_argument("file", help="Path to the log file")
    timeline_parser.add_argument("--by", choices=["minute", "hour", "day"], default="hour", help="Timeline granularity")
    timeline_parser.add_argument("--format", choices=["apache", "nginx", "json"], default="apache", help="Log format")
    timeline_parser.add_argument("--json", action="store_true", help="Output timeline in JSON format")

    # Detect Anomaly Command
    anomaly_parser = subparsers.add_parser("detect-anomaly", help="Detect traffic spikes and latency issues")
    anomaly_parser.add_argument("file", help="Path to the log file")
    anomaly_parser.add_argument("--format", choices=["apache", "nginx", "json"], default="apache", help="Log format")
    anomaly_parser.add_argument("--json", action="store_true", help="Output anomalies in JSON format")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "analyze":
        run_analyze(args)
    elif args.command == "timeline":
        run_timeline(args)
    elif args.command == "detect-anomaly":
        run_detect_anomaly(args)

if __name__ == "__main__":
    main()
