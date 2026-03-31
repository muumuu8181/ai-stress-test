import pytest

from src.ast_nodes import TokenType
from src.lexer import Lexer


def test_lexer_arithmetic():
    lexer = Lexer("1 + 2 * 3 / 4 - 5")
    tokens = lexer.tokenize()
    types = [t.type for t in tokens]
    expected = [
        TokenType.NUMBER,
        TokenType.PLUS,
        TokenType.NUMBER,
        TokenType.MULTIPLY,
        TokenType.NUMBER,
        TokenType.DIVIDE,
        TokenType.NUMBER,
        TokenType.MINUS,
        TokenType.NUMBER,
        TokenType.EOF,
    ]
    assert types == expected


def test_lexer_parentheses():
    lexer = Lexer("(1 + 2) * 3")
    tokens = lexer.tokenize()
    types = [t.type for t in tokens]
    expected = [
        TokenType.LPAREN,
        TokenType.NUMBER,
        TokenType.PLUS,
        TokenType.NUMBER,
        TokenType.RPAREN,
        TokenType.MULTIPLY,
        TokenType.NUMBER,
        TokenType.EOF,
    ]
    assert types == expected


def test_lexer_assignment_and_function():
    lexer = Lexer("x = sin(0.5)")
    tokens = lexer.tokenize()
    types = [t.type for t in tokens]
    expected = [
        TokenType.IDENTIFIER,
        TokenType.ASSIGN,
        TokenType.IDENTIFIER,
        TokenType.LPAREN,
        TokenType.NUMBER,
        TokenType.RPAREN,
        TokenType.EOF,
    ]
    assert types == expected


def test_lexer_unexpected_char():
    lexer = Lexer("1 @ 2")
    with pytest.raises(ValueError, match="Unexpected character: @"):
        lexer.tokenize()
