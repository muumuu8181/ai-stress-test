from typing import Any, List, Callable
from html import escape

def upper_filter(value: Any) -> str:
    """Converts a value to uppercase."""
    return str(value).upper()

def currency_filter(value: Any) -> str:
    """Formats a value as currency ($X.XX)."""
    try:
        num = float(value)
        return f"${num:,.2f}"
    except (ValueError, TypeError):
        return str(value)

def join_filter(value: Any, arg: str = ", ") -> str:
    """Joins a list into a string with a separator."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        return str(arg).join(str(v) for v in value)
    except (TypeError, ValueError):
        return str(value)

class SafeString(str):
    """A string that is marked as safe and should not be auto-escaped."""
    def __html__(self):
        return self

def safe_filter(value: Any) -> SafeString:
    """Marks a value as safe for HTML rendering."""
    return SafeString(value)

DEFAULT_FILTERS = {
    "upper": upper_filter,
    "currency": currency_filter,
    "join": join_filter,
    "safe": safe_filter,
}
