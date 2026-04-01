import re
import json
from abc import ABC, abstractmethod
from typing import Iterable, Optional, Dict, Any, Union
from datetime import datetime
from .models import LogEntry

class BaseParser(ABC):
    """Base class for all log parsers."""
    @abstractmethod
    def parse_line(self, line: str) -> Optional[LogEntry]:
        """
        Parses a single line of log.

        Args:
            line: A raw log line.

        Returns:
            A LogEntry object if parsing was successful, otherwise None.
        """
        pass

class CustomRegexParser(BaseParser):
    """
    Parser that uses a user-defined regex and mapping to extract fields.
    """
    def __init__(self, pattern: str, mapping: Optional[Dict[str, str]] = None, date_format: Optional[str] = None):
        """
        Initializes the parser with a regex pattern.

        Args:
            pattern: The regex pattern with named groups.
            mapping: A dictionary mapping regex group names to LogEntry attributes.
            date_format: The format of the timestamp field if it needs parsing.
        """
        self.pattern = re.compile(pattern)
        self.mapping = mapping or {}
        self.date_format = date_format

    def parse_line(self, line: str) -> Optional[LogEntry]:
        line = line.strip()
        if not line:
            return None

        match = self.pattern.match(line)
        if not match:
            return None

        groups = match.groupdict()
        entry = LogEntry(raw=line)

        for key, val in groups.items():
            mapped_key = self.mapping.get(key, key)

            if mapped_key == "timestamp":
                if self.date_format:
                    try:
                        entry.timestamp = datetime.strptime(val, self.date_format)
                    except ValueError:
                        entry.timestamp = val
                else:
                    entry.timestamp = val
            elif mapped_key == "status":
                try:
                    entry.status = int(val)
                except (ValueError, TypeError):
                    entry.status = None
            elif mapped_key == "latency":
                try:
                    entry.latency = float(val)
                except (ValueError, TypeError):
                    entry.latency = None
            elif hasattr(entry, mapped_key) and mapped_key != "metadata":
                setattr(entry, mapped_key, val)
            else:
                entry.metadata[mapped_key] = val

        return entry

class JSONParser(BaseParser):
    """
    Parser for JSON Lines format.
    """
    def __init__(self, mapping: Optional[Dict[str, str]] = None, date_format: Optional[str] = None):
        """
        Initializes the JSON parser.

        Args:
            mapping: Mapping from JSON keys to LogEntry attributes.
            date_format: The format of the timestamp field if it needs parsing.
        """
        self.mapping = mapping or {
            "timestamp": "timestamp",
            "level": "level",
            "message": "message",
            "ip": "ip",
            "status": "status",
            "latency": "latency"
        }
        self.date_format = date_format

    def parse_line(self, line: str) -> Optional[LogEntry]:
        line = line.strip()
        if not line:
            return None

        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None

        entry = LogEntry(raw=line)

        for json_key, attr_key in self.mapping.items():
            if json_key in data:
                val = data[json_key]
                if attr_key == "timestamp":
                    if self.date_format and isinstance(val, str):
                        try:
                            entry.timestamp = datetime.strptime(val, self.date_format)
                        except ValueError:
                            entry.timestamp = val
                    else:
                        entry.timestamp = val
                elif attr_key == "status":
                    try:
                        entry.status = int(val)
                    except (ValueError, TypeError):
                        entry.status = None
                elif attr_key == "latency":
                    try:
                        entry.latency = float(val)
                    except (ValueError, TypeError):
                        entry.latency = None
                elif hasattr(entry, attr_key) and attr_key != "metadata":
                    setattr(entry, attr_key, val)
                else:
                    entry.metadata[attr_key] = val

        # Add everything else to metadata if not already mapped
        mapped_json_keys = self.mapping.keys()
        for k, v in data.items():
            if k not in mapped_json_keys:
                entry.metadata[k] = v

        return entry

class ApacheCombinedParser(CustomRegexParser):
    """Parser for Apache Combined log format."""
    PATTERN = r'(?P<ip>\S+) (?P<ident>\S+) (?P<user>\S+) \[(?P<timestamp>.*?)\] "(?P<method>\S+) (?P<path>\S+) (?P<protocol>\S+)" (?P<status>\d+) (?P<size>\S+) "(?P<referrer>.*?)" "(?P<user_agent>.*?)"'
    MAPPING = {
        "timestamp": "timestamp",
        "ip": "ip",
        "method": "method",
        "path": "path",
        "status": "status",
        "size": "size",
        "referrer": "referrer",
        "user_agent": "user_agent"
    }
    DATE_FORMAT = "%d/%b/%Y:%H:%M:%S %z"

    def __init__(self):
        super().__init__(self.PATTERN, self.MAPPING, self.DATE_FORMAT)

class NginxParser(ApacheCombinedParser):
    """Nginx default log format is often similar to Apache Combined."""
    pass
