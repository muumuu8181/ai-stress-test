import pytest
from regexengine.lexer import Lexer, TokenType

def test_lexer_simple():
    lexer = Lexer("abc")
    tokens = lexer.tokenize()
    assert len(tokens) == 4 # a, b, c, EOF
    assert tokens[0].type == TokenType.LITERAL
    assert tokens[0].value == 'a'
    assert tokens[3].type == TokenType.EOF

def test_lexer_special_chars():
    lexer = Lexer(".^$*+?{}[]()|")
    tokens = lexer.tokenize()
    types = [t.type for t in tokens]
    expected = [
        TokenType.DOT, TokenType.CARET, TokenType.DOLLAR, TokenType.STAR,
        TokenType.PLUS, TokenType.QUESTION, TokenType.LBRACE, TokenType.RBRACE,
        TokenType.LBRACKET, TokenType.RBRACKET, TokenType.LPAREN, TokenType.RPAREN,
        TokenType.PIPE, TokenType.EOF
    ]
    assert types == expected

def test_lexer_escaped():
    lexer = Lexer(r"\.\[\d")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.ESCAPED
    assert tokens[0].value == '.'
    assert tokens[1].type == TokenType.ESCAPED
    assert tokens[1].value == '['
    assert tokens[2].type == TokenType.ESCAPED
    assert tokens[2].value == 'd'

def test_lexer_trailing_backslash():
    lexer = Lexer("\\")
    with pytest.raises(ValueError, match="Trailing backslash"):
        lexer.tokenize()
