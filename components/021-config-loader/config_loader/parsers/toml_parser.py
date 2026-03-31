try:
    import tomllib
except ImportError:
    # tomllib is only in stdlib since Python 3.11
    # For older versions, we can try to fall back to 'toml' or 'tomli'
    # but the requirement is stdlib ONLY.
    # Since the sandbox is Python 3.12, we should be fine,
    # but for true robustness we could provide a basic custom parser
    # if it's not present, or just let it fail if not in stdlib.
    tomllib = None

from typing import Any, Dict

def parse_toml(content: str) -> Dict[str, Any]:
    """
    Parses a TOML string into a dictionary using standard tomllib.

    Args:
        content (str): The TOML string to parse.

    Returns:
        Dict[str, Any]: The parsed dictionary.

    Raises:
        ImportError: If Python version is < 3.11 and no alternative is available.
        tomllib.TOMLDecodeError: If the content is not valid TOML.
    """
    if not content.strip():
        return {}
    if tomllib is None:
        raise ImportError("TOML support requires Python 3.11+ (tomllib in standard library)")
    return tomllib.loads(content)
