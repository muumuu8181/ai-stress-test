import json
from typing import Any, Dict

def parse_json(content: str) -> Dict[str, Any]:
    """
    Parses a JSON string into a dictionary.

    Args:
        content (str): The JSON string to parse.

    Returns:
        Dict[str, Any]: The parsed dictionary.

    Raises:
        json.JSONDecodeError: If the content is not valid JSON.
    """
    if not content.strip():
        return {}
    return json.loads(content)
