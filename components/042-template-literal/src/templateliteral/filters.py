import html
from typing import Any, Callable, Dict

class SafeString(str):
    """A string that is marked as safe and should not be auto-escaped."""
    pass

def escape_html(text: Any) -> str:
    """Escapes HTML special characters."""
    if isinstance(text, SafeString):
        return text
    return html.escape(str(text))

def upper_filter(value: Any) -> str:
    """Converts a string to uppercase."""
    return str(value).upper()

def currency_filter(value: Any) -> str:
    """Formats a number as currency."""
    try:
        amount = float(value)
        return f"${amount:,.2f}"
    except (ValueError, TypeError):
        return str(value)

def safe_filter(value: Any) -> SafeString:
    """Marks a string as safe, preventing auto-escaping."""
    return SafeString(str(value))

DEFAULT_FILTERS: Dict[str, Callable[[Any], Any]] = {
    "upper": upper_filter,
    "currency": currency_filter,
    "safe": safe_filter,
}
