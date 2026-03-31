import pytest
from templateengine.lexer import Lexer, TokenType

def test_lexer_text():
    lexer = Lexer("Hello, world!")
    tokens = lexer.tokenize()
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.TEXT
    assert tokens[0].value == "Hello, world!"
    assert tokens[0].line == 1
    assert tokens[0].column == 1

def test_lexer_variable():
    lexer = Lexer("Hello, {{ name }}!")
    tokens = lexer.tokenize()
    assert len(tokens) == 5
    assert tokens[1].type == TokenType.VAR_START
    assert tokens[2].type == TokenType.EXPRESSION
    assert tokens[2].value == " name "
    assert tokens[3].type == TokenType.VAR_END

def test_lexer_block():
    lexer = Lexer("{% if True %}Yes{% endif %}")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.BLOCK_START
    assert tokens[1].type == TokenType.EXPRESSION
    assert tokens[1].value == " if True "
    assert tokens[2].type == TokenType.BLOCK_END
    assert tokens[3].type == TokenType.TEXT
    assert tokens[3].value == "Yes"

def test_lexer_comment():
    lexer = Lexer("A{# comment #}B")
    tokens = lexer.tokenize()
    assert len(tokens) == 3
    assert tokens[1].type == TokenType.COMMENT
    assert tokens[1].value == " comment "

def test_lexer_multiline():
    lexer = Lexer("Line 1\nLine 2\n{{ var }}")
    tokens = lexer.tokenize()
    assert tokens[0].type == TokenType.TEXT
    assert tokens[1].type == TokenType.VAR_START
    assert tokens[1].line == 3
    assert tokens[1].column == 1

def test_lexer_unclosed_tag():
    lexer = Lexer("{{ unclosed")
    with pytest.raises(SyntaxError) as exc:
        lexer.tokenize()
    assert "Unclosed tag" in str(exc.value)
