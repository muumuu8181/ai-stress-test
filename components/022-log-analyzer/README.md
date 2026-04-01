# Logalyzer - Log File Analyzer

A pure Python log file analyzer that supports multiple formats, filtering, aggregation, and anomaly detection.

## Features

- **Supported Formats:** Apache Combined, Nginx, JSON lines, and Custom Regex.
- **Filtering:** Level, time range, keywords, and regular expressions.
- **Aggregation:** Error rates, response time statistics (min, max, avg, p95), IP-based access counts, and top paths.
- **Anomaly Detection:** Traffic spikes and latency increases.
- **Timeline:** Configurable granularity (minute, hour, day).
- **Streaming:** Efficiently processes large files line-by-line.
- **Reports:** Text-based summary or JSON output.

## Installation

Ensure you have Python 3.8+ installed. No external dependencies are required for the core functionality.

## Usage

### Analyze a log file

```bash
python3 -m logalyzer analyze access.log --format apache --top-errors 10
```

### Show a timeline of events

```bash
python3 -m logalyzer timeline app.log --format json --by hour
```

### Detect anomalies

```bash
python3 -m logalyzer detect-anomaly access.log --format nginx
```

### Filtering examples

```bash
# Filter by log level
python3 -m logalyzer analyze app.log --format json --level ERROR

# Filter by keyword
python3 -m logalyzer analyze access.log --keyword "bot"

# Custom regex filter
python3 -m logalyzer analyze access.log --regex "/api/v2/.*"
```

### Output as JSON

```bash
python3 -m logalyzer analyze access.log --json > report.json
```

## Custom Regex Parsing

To parse a custom log format, use the `--format custom` and `--custom-pattern` flags. The pattern must use named groups that match `LogEntry` attributes (`timestamp`, `level`, `message`, `ip`, `status`, `latency`).

```bash
python3 -m logalyzer analyze my.log --format custom --custom-pattern '(?P<timestamp>.*) \[(?P<level>.*)\] (?P<message>.*)'
```

## Running Tests

```bash
PYTHONPATH=src pytest tests/
```
