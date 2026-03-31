import datetime
from typing import Any, Dict, List, Union
from .datetime_util import format_toml_datetime

def dumps(data: Dict[str, Any]) -> str:
    """
    Serializes a dictionary to a TOML-compliant string.
    """
    return _dump_table(data)

def _dump_table(data: Dict[str, Any], prefix: str = "") -> str:
    lines = []

    # First, handle non-dict values
    for key, value in data.items():
        if not isinstance(value, (dict, list)):
            lines.append(f"{_escape_key(key)} = {_dump_value(value)}")
        elif isinstance(value, list):
            if not value or not all(isinstance(v, dict) for v in value):
                lines.append(f"{_escape_key(key)} = {_dump_value(value)}")

    # Handle nested tables
    for key, value in data.items():
        if isinstance(value, dict):
            new_prefix = f"{prefix}.{_escape_key(key)}" if prefix else _escape_key(key)
            lines.append(f"\n[{new_prefix}]")
            table_content = _dump_table(value, new_prefix)
            if table_content:
                lines.append(table_content)
        elif isinstance(value, list) and all(isinstance(v, dict) for v in value):
            new_prefix = f"{prefix}.{_escape_key(key)}" if prefix else _escape_key(key)
            for item in value:
                lines.append(f"\n[[{new_prefix}]]")
                table_content = _dump_table(item, new_prefix)
                if table_content:
                    lines.append(table_content)

    return "\n".join(lines).strip()

def _escape_key(key: str) -> str:
    if all(c.isalnum() or c in '-_' for c in key):
        return key
    return f'"{_escape_string(key)}"'

import math

def _dump_value(value: Any) -> str:
    if isinstance(value, str):
        return f'"{_escape_string(value)}"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, float):
        if math.isnan(value):
            return "nan"
        elif math.isinf(value):
            return "inf" if value > 0 else "-inf"
        return str(value)
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return format_toml_datetime(value)
    elif isinstance(value, list):
        items = [_dump_value(v) for v in value]
        return f"[ {', '.join(items)} ]"
    elif isinstance(value, dict):
        # This would be an inline table if used in a list or elsewhere
        items = [f"{_escape_key(k)} = {_dump_value(v)}" for k, v in value.items()]
        return f"{{ {', '.join(items)} }}"
    else:
        raise TypeError(f"Object of type {type(value)} is not TOML serializable")

def _escape_string(s: str) -> str:
    escapes = {
        '\b': '\\b', '\t': '\\t', '\n': '\\n', '\f': '\\f', '\r': '\\r', '"': '\\"', '\\': '\\\\'
    }
    res = ""
    for char in s:
        if char in escapes:
            res += escapes[char]
        elif ord(char) < 32:
            res += f"\\u{ord(char):04x}"
        else:
            res += char
    return res
