from typing import Any, Dict, IO, Union
from .lexer import Lexer
from .parser import Parser
from .writer import dumps as dumps_internal

def loads(s: str) -> Dict[str, Any]:
    """
    Parses a TOML string into a dictionary.

    Args:
        s: The TOML string to parse.

    Returns:
        A dictionary representation of the TOML string.
    """
    lexer = Lexer(s)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()

def load(fp: IO[str]) -> Dict[str, Any]:
    """
    Parses a TOML file-like object into a dictionary.

    Args:
        fp: A file-like object containing TOML.

    Returns:
        A dictionary representation of the TOML content.
    """
    return loads(fp.read())

def dumps(data: Dict[str, Any]) -> str:
    """
    Serializes a dictionary to a TOML-compliant string.

    Args:
        data: The dictionary to serialize.

    Returns:
        A TOML-compliant string.
    """
    return dumps_internal(data)

def dump(data: Dict[str, Any], fp: IO[str]) -> None:
    """
    Serializes a dictionary to a TOML file-like object.

    Args:
        data: The dictionary to serialize.
        fp: A file-like object to write the TOML content to.
    """
    fp.write(dumps(data))
