import datetime
import re
from typing import Union

# Regex for TOML datetime formats
# Offset Date-Time: 1979-05-27T07:32:00Z, 1979-05-27T00:32:00-07:00, 1979-05-27T00:32:00.999999-07:00
OFFSET_DATETIME_RE = re.compile(r'^(\d{4}-\d{2}-\d{2})[Tt ](\d{2}:\d{2}:\d{2}(?:\.\d+)?)([Zz]|[+-]\d{2}:\d{2})$')
# Local Date-Time: 1979-05-27T07:32:00, 1979-05-27T00:32:00.999999
LOCAL_DATETIME_RE = re.compile(r'^(\d{4}-\d{2}-\d{2})[Tt ](\d{2}:\d{2}:\d{2}(?:\.\d+)?)$')
# Local Date: 1979-05-27
LOCAL_DATE_RE = re.compile(r'^(\d{4}-\d{2}-\d{2})$')
# Local Time: 07:32:00, 00:32:00.999999
LOCAL_TIME_RE = re.compile(r'^(\d{2}:\d{2}:\d{2}(?:\.\d+)?)$')

def parse_toml_datetime(s: str) -> Union[datetime.datetime, datetime.date, datetime.time, None]:
    """
    Parses a TOML datetime string into a Python datetime object.

    Args:
        s: The TOML datetime string.

    Returns:
        A datetime.datetime, datetime.date, or datetime.time object, or None if the string is not a valid TOML datetime.
    """
    # Offset Date-Time
    match = OFFSET_DATETIME_RE.match(s)
    if match:
        date_part, time_part, offset_part = match.groups()
        if offset_part.upper() == 'Z':
            offset_part = '+00:00'

        # TOML permits higher precision fractional seconds (with truncation to microseconds)
        if '.' in time_part:
            base_time, frac = time_part.split('.')
            if len(frac) > 6:
                time_part = f"{base_time}.{frac[:6]}"

        # Python's fromisoformat handles microseconds and offsets
        try:
            return datetime.datetime.fromisoformat(f"{date_part}T{time_part}{offset_part}")
        except ValueError:
            return None

    # Local Date-Time
    match = LOCAL_DATETIME_RE.match(s)
    if match:
        dt_str = s.replace(' ', 'T')
        if '.' in dt_str:
            base_dt, frac = dt_str.split('.')
            if len(frac) > 6:
                dt_str = f"{base_dt}.{frac[:6]}"
        try:
            return datetime.datetime.fromisoformat(dt_str)
        except ValueError:
            return None

    # Local Date
    match = LOCAL_DATE_RE.match(s)
    if match:
        try:
            return datetime.date.fromisoformat(s)
        except ValueError:
            return None

    # Local Time
    match = LOCAL_TIME_RE.match(s)
    if match:
        t_str = s
        if '.' in t_str:
            base_t, frac = t_str.split('.')
            if len(frac) > 6:
                t_str = f"{base_t}.{frac[:6]}"
        try:
            return datetime.time.fromisoformat(t_str)
        except ValueError:
            return None

    return None

def format_toml_datetime(dt: Union[datetime.datetime, datetime.date, datetime.time]) -> str:
    """
    Formats a Python datetime object into a TOML-compliant datetime string.

    Args:
        dt: A datetime.datetime, datetime.date, or datetime.time object.

    Returns:
        A TOML-compliant datetime string.
    """
    if isinstance(dt, datetime.datetime):
        s = dt.isoformat()
        if s.endswith('+00:00'):
            s = s[:-6] + 'Z'
        return s
    elif isinstance(dt, datetime.date):
        return dt.isoformat()
    elif isinstance(dt, datetime.time):
        return dt.isoformat()
    else:
        raise TypeError(f"Expected datetime, date, or time object, got {type(dt)}")
