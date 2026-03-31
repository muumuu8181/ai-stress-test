import os
import re
from typing import Any, Dict

def parse_env(content: str) -> Dict[str, Any]:
    """
    Parses a .env string into a dictionary.
    Supports basic KEY=VALUE, comments (#), and optional quotes.

    Args:
        content (str): The .env string to parse.

    Returns:
        Dict[str, Any]: The parsed dictionary.
    """
    result: Dict[str, Any] = {}
    lines = content.splitlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # Basic KEY=VALUE parsing
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes if present
            if len(value) >= 2 and ((value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'")):
                value = value[1:-1]

            result[key] = value

    return result
