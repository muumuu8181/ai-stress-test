import pytest
from datetime import datetime
from logalyzer.parsers import JSONParser, ApacheCombinedParser, CustomRegexParser, NginxParser

def test_json_parser():
    parser = JSONParser()
    line = '{"timestamp": "2023-01-01T12:00:00", "level": "INFO", "message": "Hello world", "ip": "1.2.3.4", "status": 200, "latency": 0.123, "user": "alice"}'
    entry = parser.parse_line(line)

    assert entry.timestamp == "2023-01-01T12:00:00"
    assert entry.level == "INFO"
    assert entry.message == "Hello world"
    assert entry.ip == "1.2.3.4"
    assert entry.status == 200
    assert entry.latency == 0.123
    assert entry.get("user") == "alice"
    assert entry.raw == line

def test_json_parser_malformed():
    parser = JSONParser()
    assert parser.parse_line('invalid json') is None
    assert parser.parse_line('') is None

def test_apache_parser():
    parser = ApacheCombinedParser()
    line = '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "http://www.example.com/start.html" "Mozilla/4.08 [en] (Win98; I ;Nav)"'
    entry = parser.parse_line(line)

    assert entry.ip == "127.0.0.1"
    assert isinstance(entry.timestamp, datetime)
    assert entry.status == 200
    assert entry.get("method") == "GET"
    assert entry.get("path") == "/apache_pb.gif"
    assert entry.get("size") == "2326"

def test_custom_regex_parser():
    pattern = r'(?P<time>\d{4}-\d{2}-\d{2}) \[(?P<lvl>\w+)\] (?P<msg>.*)'
    mapping = {"time": "timestamp", "lvl": "level", "msg": "message"}
    parser = CustomRegexParser(pattern, mapping)

    line = '2023-05-20 [ERROR] Connection failed'
    entry = parser.parse_line(line)

    assert entry.timestamp == "2023-05-20"
    assert entry.level == "ERROR"
    assert entry.message == "Connection failed"

def test_nginx_parser():
    # Nginx default is often similar to Apache Combined
    parser = NginxParser()
    line = '192.168.1.1 - - [20/May/2023:10:00:00 +0000] "GET /api/v1/resource HTTP/1.1" 404 150 "-" "Go-http-client/1.1"'
    entry = parser.parse_line(line)
    assert entry.ip == "192.168.1.1"
    assert entry.status == 404
    assert entry.get("path") == "/api/v1/resource"
