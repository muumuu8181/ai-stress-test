import re
from typing import Callable, Dict

# Simple regex for email (not fully RFC 5322 but common for standard validations)
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# Basic URI regex (RFC 3986)
URI_REGEX = re.compile(
    r"^(?:[a-z][a-z0-9+.-]*:)"  # Scheme
    r"(?://(?:(?:[a-z0-9._~%!$&'()*+,;=:-]|%[0-9a-f]{2})*@)?"  # Userinfo
    r"(?:(?:[a-z0-9._~%!$&'()*+,;=:-]|%[0-9a-f]{2})*)"  # Host
    r"(?::[0-9]*)?)?"  # Port
    r"(?:/(?:[a-z0-9._~%!$&'()*+,;=:-]|%[0-9a-f]{2})*)*"  # Path
    r"(?:\?(?:[a-z0-9._~%!$&'()*+,;=:-?/@]|%[0-9a-f]{2})*)?"  # Query
    r"(?:#(?:[a-z0-9._~%!$&'()*+,;=:-?/@]|%[0-9a-f]{2})*)?$",  # Fragment
    re.IGNORECASE
)

# Date regex (ISO 8601 YYYY-MM-DD)
DATE_REGEX = re.compile(r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$")

def validate_email(instance: str) -> bool:
    """Validates if the instance is a valid email string."""
    return bool(EMAIL_REGEX.match(instance))

def validate_uri(instance: str) -> bool:
    """Validates if the instance is a valid URI."""
    return bool(URI_REGEX.match(instance))

def validate_date(instance: str) -> bool:
    """Validates if the instance is a valid date (YYYY-MM-DD)."""
    return bool(DATE_REGEX.match(instance))

FORMAT_VALIDATORS: Dict[str, Callable[[str], bool]] = {
    "email": validate_email,
    "uri": validate_uri,
    "date": validate_date,
}
