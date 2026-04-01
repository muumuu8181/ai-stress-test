import pytest
import subprocess, os, json
from datetime import datetime

@pytest.fixture
def json_log(tmp_path):
    p = tmp_path / "app.log"
    p.write_text('{"timestamp": "2023-01-01T10:00:00Z", "level": "INFO", "latency": 0.1}\n{"timestamp": "2023-01-01T10:01:00Z", "level": "ERROR", "latency": 2.0}\n')
    return str(p)

def run(args):
    e = os.environ.copy(); e["PYTHONPATH"] = "components/022-log-analyzer/src"
    return subprocess.run(["python3", "-m", "logalyzer"] + args, env=e, capture_output=True, text=True)

def test_cli_analyze(json_log):
    r = run(["analyze", json_log, "--format", "json", "--json"])
    assert r.returncode == 0
    assert json.loads(r.stdout)["total_count"] == 2

def test_cli_detect_anomaly(json_log):
    r = run(["detect-anomaly", json_log, "--format", "json"])
    assert r.returncode == 0
    assert "Latency Increases Detected" in r.stdout

def test_cli_p2_validation():
    r = run(["analyze", "dummy", "--format", "custom"])
    assert r.returncode == 1
    assert "Error: --custom-pattern is required" in r.stderr
