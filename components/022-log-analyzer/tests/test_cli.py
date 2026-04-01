import pytest
import subprocess
import os
import json
from datetime import datetime

@pytest.fixture
def apache_log_file(tmp_path):
    log_content = (
        '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "-" "Mozilla/4.08"\n'
        '127.0.0.1 - frank [10/Oct/2000:13:56:36 -0700] "GET /test.html HTTP/1.0" 404 100 "-" "Mozilla/4.08"\n'
        '192.168.1.1 - - [10/Oct/2000:13:57:36 -0700] "POST /api HTTP/1.1" 200 50 "-" "curl/7.64.1"\n'
    )
    p = tmp_path / "access.log"
    p.write_text(log_content)
    return str(p)

@pytest.fixture
def json_log_file(tmp_path):
    log_content = (
        '{"timestamp": "2023-01-01T10:00:00", "level": "INFO", "message": "Success", "status": 200, "latency": 0.05}\n'
        '{"timestamp": "2023-01-01T10:00:01", "level": "INFO", "message": "Success", "status": 200, "latency": 0.05}\n'
        '{"timestamp": "2023-01-01T10:00:02", "level": "INFO", "message": "Success", "status": 200, "latency": 0.05}\n'
        '{"timestamp": "2023-01-01T10:01:00", "level": "ERROR", "message": "Failure", "status": 500, "latency": 2.0}\n'
    )
    p = tmp_path / "app.log"
    p.write_text(log_content)
    return str(p)

def run_logalyzer(args):
    env = os.environ.copy()
    env["PYTHONPATH"] = "components/022-log-analyzer/src"
    result = subprocess.run(
        ["python3", "-m", "logalyzer"] + args,
        env=env,
        capture_output=True,
        text=True
    )
    return result

def test_cli_analyze_apache(apache_log_file):
    result = run_logalyzer(["analyze", apache_log_file, "--format", "apache"])
    assert result.returncode == 0
    assert "Total Entries Processed: 3" in result.stdout
    assert "127.0.0.1: 2" in result.stdout
    assert "404: 1" in result.stdout

def test_cli_analyze_json_output(json_log_file):
    result = run_logalyzer(["analyze", json_log_file, "--format", "json", "--json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["total_count"] == 4
    assert data["levels"]["INFO"] == 3
    assert data["levels"]["ERROR"] == 1
    assert data["latency_stats"]["max"] == 2.0

def test_cli_timeline(apache_log_file):
    result = run_logalyzer(["timeline", apache_log_file, "--format", "apache", "--by", "hour"])
    assert result.returncode == 0
    assert "2000-10-10 13:00" in result.stdout
    assert "(3)" in result.stdout

def test_cli_detect_anomaly(json_log_file):
    result = run_logalyzer(["detect-anomaly", json_log_file, "--format", "json"])
    assert result.returncode == 0
    assert "Latency Increases Detected" in result.stdout

def test_cli_filtering_time_range(json_log_file):
    # Only the entries between 10:00:00 and 10:00:01 (2 entries)
    result = run_logalyzer(["analyze", json_log_file, "--format", "json", "--start", "2023-01-01T10:00:00", "--end", "2023-01-01T10:00:01", "--json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["total_count"] == 2

def test_cli_custom_pattern(tmp_path):
    log_content = "2023-05-20 [ERROR] App failed\n"
    p = tmp_path / "custom.log"
    p.write_text(log_content)

    pattern = '(?P<timestamp>.*) \[(?P<level>.*)\] (?P<message>.*)'
    result = run_logalyzer(["analyze", str(p), "--format", "custom", "--custom-pattern", pattern, "--json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["total_count"] == 1
    assert data["levels"]["ERROR"] == 1
