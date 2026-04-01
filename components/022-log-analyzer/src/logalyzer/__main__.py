import sys
import argparse
import json
from collections import defaultdict
from typing import Optional, List, Dict, Any, Iterable
from datetime import datetime
from .parsers import BaseParser, ApacheCombinedParser, NginxParser, JSONParser, CustomRegexParser
from .filters import LogFilter, level_filter, keyword_filter, regex_filter, time_range_filter
from .aggregator import LogAggregator
from .analysis import AnomalyDetector
from .models import LogEntry

def get_parser(format_name: str, custom_pattern: Optional[str] = None) -> BaseParser:
    if format_name == "apache": return ApacheCombinedParser()
    elif format_name == "nginx": return NginxParser()
    elif format_name == "json": return JSONParser()
    elif format_name == "custom":
        if not custom_pattern:
            print("Error: --custom-pattern is required when format is 'custom'.", file=sys.stderr)
            sys.exit(1)
        return CustomRegexParser(custom_pattern)
    return ApacheCombinedParser()

def stream_logs(file_path: str, parser: BaseParser, filters: LogFilter) -> Iterable[LogEntry]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                entry = parser.parse_line(line)
                if entry and filters(entry): yield entry
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr); sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr); sys.exit(1)

def parse_date_arg(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str: return None
    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
        try: return datetime.strptime(date_str, fmt)
        except ValueError: continue
    return None

def build_filters(args) -> LogFilter:
    filters = LogFilter()
    if getattr(args, "level", None): filters.add(level_filter(args.level))
    if getattr(args, "keyword", None): filters.add(keyword_filter(args.keyword))
    if getattr(args, "regex", None): filters.add(regex_filter(args.regex))
    start = parse_date_arg(getattr(args, "start", None))
    end = parse_date_arg(getattr(args, "end", None))
    if start or end: filters.add(time_range_filter(start, end))
    return filters

def run_analyze(args):
    parser_inst = get_parser(args.format, args.custom_pattern)
    filters = build_filters(args)
    aggregator = LogAggregator()
    for entry in stream_logs(args.file, parser_inst, filters): aggregator.add(entry)
    summary = aggregator.get_summary(top_n=args.top_errors)
    if args.json: print(json.dumps(summary, indent=2, default=str))
    else:
        print("=== Log Analysis Report ===")
        print(f"File: {args.file}"); print(f"Total Entries Processed: {summary['total_count']}"); print(f"Error Rate: {summary['error_rate']:.2%}")
        print("\nLog Levels:"); [print(f"  {k}: {v}") for k,v in summary['levels'].items()]
        print(f"\nTop {args.top_errors} IPs:"); [print(f"  {k}: {v}") for k,v in summary.get(f"top_{args.top_errors}_ips", {}).items()]
        print(f"\nTop {args.top_errors} Errors:"); [print(f"  {k}: {v}") for k,v in summary.get(f"top_{args.top_errors}_errors", {}).items()]
        if "latency_stats" in summary:
            s = summary["latency_stats"]
            print("\nResponse Time Statistics:"); print(f"  Min: {s['min']:.4f}"); print(f"  Max: {s['max']:.4f}"); print(f"  Avg: {s['avg']:.4f}")
            if "p95_approx" in s: print(f"  p95 (approx): {s['p95_approx']:.4f}")

def run_timeline(args):
    parser_inst = get_parser(args.format, args.custom_pattern)
    filters = build_filters(args)
    aggregator = LogAggregator()
    for entry in stream_logs(args.file, parser_inst, filters): aggregator.add(entry, timeline_by=args.by)
    summary = aggregator.get_summary()
    timeline = summary.get("timeline", {})
    if args.json: print(json.dumps(timeline, indent=2))
    else:
        print(f"=== Timeline (by {args.by}) ===")
        if timeline:
            max_v = max(timeline.values())
            for k, v in timeline.items(): print(f"{k}: {'#' * (v * 50 // max_v if max_v > 0 else 0)} ({v})")

def run_detect_anomaly(args):
    parser_inst = get_parser(args.format, args.custom_pattern)
    filters = build_filters(args)
    detector = AnomalyDetector(); aggregator = LogAggregator()
    latency_summaries = defaultdict(lambda: {"count": 0, "sum": 0.0})
    for entry in stream_logs(args.file, parser_inst, filters):
        aggregator.add(entry, timeline_by="minute")
        if entry.latency is not None and entry.timestamp and isinstance(entry.timestamp, datetime):
            key = entry.timestamp.strftime("%Y-%m-%d %H:%M")
            latency_summaries[key]["count"] += 1; latency_summaries[key]["sum"] += entry.latency
    summary = aggregator.get_summary(); spikes = detector.detect_spikes(summary.get("timeline", {}))
    mock_entries = []
    for t_str, data in latency_summaries.items():
        if data["count"] > 0: mock_entries.append(LogEntry(timestamp=datetime.strptime(t_str, "%Y-%m-%d %H:%M"), latency=data["sum"]/data["count"]))
    latency_spikes = detector.detect_latency_spikes(mock_entries)
    res = {"spikes": spikes, "latency_anomalies": latency_spikes}
    if args.json: print(json.dumps(res, indent=2))
    else:
        print("=== Anomaly Detection Report ===")
        if not spikes and not latency_spikes: print("No anomalies detected.")
        if spikes:
            print("\nTraffic Spikes Detected:")
            for s in spikes: print(f"  - {s['timestamp']}: {s['count']} entries (Factor: {s['factor']:.2f}x avg)")
        if latency_spikes:
            print("\nLatency Increases Detected:")
            for s in latency_spikes: print(f"  - {s['timestamp']}: Avg {s['avg_latency']:.4f} (Factor: {s['factor']:.2f}x global avg)")

def main():
    parser = argparse.ArgumentParser(prog="logalyzer", description="Log File Analyzer")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    f_args = argparse.ArgumentParser(add_help=False)
    f_args.add_argument("--format", choices=["apache", "nginx", "json", "custom"], default="apache")
    f_args.add_argument("--custom-pattern"); f_args.add_argument("--level"); f_args.add_argument("--keyword"); f_args.add_argument("--regex")
    f_args.add_argument("--start"); f_args.add_argument("--end")
    p1 = subparsers.add_parser("analyze", parents=[f_args]); p1.add_argument("file"); p1.add_argument("--top-errors", type=int, default=10); p1.add_argument("--json", action="store_true")
    p2 = subparsers.add_parser("timeline", parents=[f_args]); p2.add_argument("file"); p2.add_argument("--by", choices=["minute", "hour", "day"], default="hour"); p2.add_argument("--json", action="store_true")
    p3 = subparsers.add_parser("detect-anomaly", parents=[f_args]); p3.add_argument("file"); p3.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.command: parser.print_help(); sys.exit(0)
    if args.command == "analyze": run_analyze(args)
    elif args.command == "timeline": run_timeline(args)
    elif args.command == "detect-anomaly": run_detect_anomaly(args)

if __name__ == "__main__": main()
