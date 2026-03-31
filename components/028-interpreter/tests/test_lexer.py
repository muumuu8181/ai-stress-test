import pytest
import sys
import os

# Workaround for the dash in the directory name
sys.path.append(os.path.join(os.getcwd(), "components/028-interpreter/src"))

from interpreter.lexer import Lexer, TokenType

def test_lexer_literals():
    source = 'let x = 10 "hello" 3.14 true false'
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()

    assert tokens[0].type == TokenType.LET
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].lexeme == "x"
    assert tokens[2].type == TokenType.EQUAL
    assert tokens[3].type == TokenType.INTEGER
    assert tokens[3].literal == 10
    assert tokens[4].type == TokenType.STRING
    assert tokens[4].literal == "hello"
    assert tokens[5].type == TokenType.FLOAT
    assert tokens[5].literal == 3.14
    assert tokens[6].type == TokenType.TRUE
    assert tokens[7].type == TokenType.FALSE
    assert tokens[8].type == TokenType.EOF

def test_lexer_operators():
    source = "+ - * / % == != < > <= >= and or not"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()

    expected = [
        TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH, TokenType.PERCENT,
        TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL, TokenType.LESS, TokenType.GREATER,
        TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL, TokenType.AND, TokenType.OR, TokenType.NOT
    ]

    for i, t in enumerate(expected):
        assert tokens[i].type == t

def test_lexer_delimiters():
    source = "( ) { } [ ] ,"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()

    expected = [
        TokenType.LEFT_PAREN, TokenType.RIGHT_PAREN, TokenType.LEFT_BRACE,
        TokenType.RIGHT_BRACE, TokenType.LEFT_BRACKET, TokenType.RIGHT_BRACKET, TokenType.COMMA
    ]

    for i, t in enumerate(expected):
        assert tokens[i].type == t

def test_lexer_error():
    with pytest.raises(SyntaxError):
        Lexer("@").scan_tokens()

def test_lexer_unterminated_string():
    with pytest.raises(SyntaxError):
        Lexer('"hello').scan_tokens()
