import tomllib
from typing import Any, Dict

def parse_toml(content: str) -> Dict[str, Any]:
    """
    Parses a TOML string into a dictionary.

    Args:
        content (str): The TOML string to parse.

    Returns:
        Dict[str, Any]: The parsed dictionary.

    Raises:
        tomllib.TOMLDecodeError: If the content is not valid TOML.
    """
    if not content.strip():
        return {}
    return tomllib.loads(content)
