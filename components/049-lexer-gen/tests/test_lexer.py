import pytest
from lexer_gen.core import BaseLexer, Token, LexerError

def test_simple_tokenizing():
    lexer = BaseLexer("123 + 456")
    lexer.add_rule("NUMBER", r"\d+")
    lexer.add_rule("PLUS", r"\+")
    lexer.add_skip_rule(r"\s+")

    tokens = list(lexer.tokenize())

    assert len(tokens) == 3
    assert tokens[0] == Token("NUMBER", "123", 1, 1, 0)
    assert tokens[1] == Token("PLUS", "+", 1, 5, 4)
    assert tokens[2] == Token("NUMBER", "456", 1, 7, 6)

def test_priority_and_longest_match():
    # Longest match
    lexer = BaseLexer("if_then_else")
    lexer.add_rule("IF", r"if")
    lexer.add_rule("IDENTIFIER", r"[a-z_]+")

    tokens = list(lexer.tokenize())
    assert len(tokens) == 1
    assert tokens[0].type == "IDENTIFIER"

    # Priority when length is equal
    lexer = BaseLexer("if")
    lexer.add_rule("IF", r"if", priority=1)
    lexer.add_rule("IDENTIFIER", r"[a-z]+")

    tokens = list(lexer.tokenize())
    assert tokens[0].type == "IF"

def test_line_column_tracking():
    lexer = BaseLexer("line1\nline2\n  line3")
    lexer.add_rule("WORD", r"\w+")
    lexer.add_skip_rule(r"\s+")

    tokens = list(lexer.tokenize())

    assert tokens[0] == Token("WORD", "line1", 1, 1, 0)
    assert tokens[1] == Token("WORD", "line2", 2, 1, 6)
    assert tokens[2] == Token("WORD", "line3", 3, 3, 14)

def test_error_recovery():
    lexer = BaseLexer("123 $ 456")
    lexer.add_rule("NUMBER", r"\d+")
    lexer.add_skip_rule(r"\s+")

    tokens = list(lexer.tokenize())

    assert len(tokens) == 2
    assert tokens[0].value == "123"
    assert tokens[1].value == "456"
    assert len(lexer.errors) == 1
    assert lexer.errors[0].line == 1
    assert lexer.errors[0].column == 5

def test_empty_match_prevention():
    lexer = BaseLexer("")
    with pytest.raises(ValueError):
        lexer.add_rule("EMPTY", r"a*")
    with pytest.raises(ValueError):
        lexer.add_skip_rule(r"b*")
