from typing import Any, List, Optional
from .lexer import Lexer
from .parser import Parser
from .evaluator import Evaluator

def find(data: Any, path: str) -> List[Any]:
    """Find values in a JSON-like object matching the given path."""
    lexer = Lexer(path)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    nodes = parser.parse()
    evaluator = Evaluator(data)
    matches = evaluator.evaluate(nodes)
    return [match.value for match in matches]

def update(data: Any, path: str, value: Any) -> Any:
    """Update values in a JSON-like object matching the given path."""
    lexer = Lexer(path)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    nodes = parser.parse()
    evaluator = Evaluator(data)
    return evaluator.update(nodes, value)

def delete(data: Any, path: str) -> Any:
    """Delete values in a JSON-like object matching the given path."""
    lexer = Lexer(path)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    nodes = parser.parse()
    evaluator = Evaluator(data)
    return evaluator.delete(nodes)
