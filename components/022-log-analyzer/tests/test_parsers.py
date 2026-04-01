import pytest
from datetime import datetime
from logalyzer.parsers import JSONParser, ApacheCombinedParser

def test_json_parser():
    parser = JSONParser()
    line = '{"timestamp": "2023-01-01T12:00:00Z", "level": "INFO", "status": 200}'
    entry = parser.parse_line(line)
    assert isinstance(entry.timestamp, datetime)
    assert entry.level == "INFO"

def test_apache_parser():
    parser = ApacheCombinedParser()
    line = '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET / HTTP/1.0" 200 2326 "-" "-"'
    entry = parser.parse_line(line)
    assert entry.ip == "127.0.0.1"
    assert entry.status == 200
