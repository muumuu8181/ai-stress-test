import configparser
import io
from typing import Any, Dict

def parse_ini(content: str) -> Dict[str, Any]:
    """
    Parses an INI string into a dictionary.

    Args:
        content (str): The INI string to parse.

    Returns:
        Dict[str, Any]: The parsed dictionary.
    """
    config = configparser.ConfigParser()
    config.read_string(content)

    result: Dict[str, Any] = {}
    for section in config.sections():
        result[section] = dict(config.items(section))

    # Handle default section if it has entries other than the ones in sections
    if config.defaults():
        result['DEFAULT'] = dict(config.defaults())

    return result
