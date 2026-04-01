import re
import json
from abc import ABC, abstractmethod
from typing import Iterable, Optional, Dict, Any, Union
from datetime import datetime
from .models import LogEntry

class BaseParser(ABC):
    @abstractmethod
    def parse_line(self, line: str) -> Optional[LogEntry]:
        pass

class CustomRegexParser(BaseParser):
    def __init__(self, pattern: str, mapping: Optional[Dict[str, str]] = None, date_format: Optional[str] = None):
        self.pattern = re.compile(pattern)
        self.mapping = mapping or {}
        self.date_format = date_format

    def parse_line(self, line: str) -> Optional[LogEntry]:
        line = line.strip()
        if not line: return None
        match = self.pattern.match(line)
        if not match: return None
        groups = match.groupdict()
        entry = LogEntry(raw=line)
        for key, val in groups.items():
            mapped_key = self.mapping.get(key, key)
            if mapped_key == "timestamp":
                if self.date_format:
                    try:
                        entry.timestamp = datetime.strptime(val, self.date_format)
                    except ValueError: entry.timestamp = val
                else: entry.timestamp = val
            elif mapped_key == "status":
                try: entry.status = int(val)
                except: entry.status = None
            elif mapped_key == "latency":
                try: entry.latency = float(val)
                except: entry.latency = None
            elif hasattr(entry, mapped_key) and mapped_key != "metadata":
                setattr(entry, mapped_key, val)
            else: entry.metadata[mapped_key] = val
        return entry

class JSONParser(BaseParser):
    def __init__(self, mapping: Optional[Dict[str, str]] = None):
        self.mapping = mapping or {"timestamp": "timestamp", "level": "level", "message": "message", "ip": "ip", "status": "status", "latency": "latency"}

    def parse_line(self, line: str) -> Optional[LogEntry]:
        line = line.strip()
        if not line: return None
        try: data = json.loads(line)
        except: return None
        entry = LogEntry(raw=line)
        for json_key, attr_key in self.mapping.items():
            if json_key in data:
                val = data[json_key]
                if attr_key == "timestamp":
                    if isinstance(val, str):
                        try:
                            ts_val = val.replace('Z', '+00:00')
                            parsed = None
                            for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                                try:
                                    parsed = datetime.strptime(ts_val, fmt)
                                    if parsed.tzinfo is not None: parsed = parsed.replace(tzinfo=None)
                                    break
                                except ValueError: continue
                            entry.timestamp = parsed if parsed else val
                        except: entry.timestamp = val
                    else: entry.timestamp = val
                elif attr_key == "status":
                    try: entry.status = int(val)
                    except: entry.status = None
                elif attr_key == "latency":
                    try: entry.latency = float(val)
                    except: entry.latency = None
                elif hasattr(entry, attr_key) and attr_key != "metadata":
                    setattr(entry, attr_key, val)
                else: entry.metadata[attr_key] = val
        for k, v in data.items():
            if k not in self.mapping: entry.metadata[k] = v
        return entry

class ApacheCombinedParser(CustomRegexParser):
    PATTERN = r'(?P<ip>\S+) (?P<ident>\S+) (?P<user>\S+) \[(?P<timestamp>.*?)\] "(?P<method>\S+) (?P<path>\S+) (?P<protocol>\S+)" (?P<status>\d+) (?P<size>\S+) "(?P<referrer>.*?)" "(?P<user_agent>.*?)"'
    MAPPING = {"timestamp": "timestamp", "ip": "ip", "method": "method", "path": "path", "status": "status", "size": "size", "referrer": "referrer", "user_agent": "user_agent"}
    DATE_FORMAT = "%d/%b/%Y:%H:%M:%S %z"
    def __init__(self): super().__init__(self.PATTERN, self.MAPPING, self.DATE_FORMAT)

class NginxParser(ApacheCombinedParser): pass
