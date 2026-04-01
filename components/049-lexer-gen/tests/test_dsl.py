import pytest
from lexer_gen.dsl import DSLParser, DSLParserError

def test_parse_simple_dsl():
    parser = DSLParser()
    dsl = r"""
    # Comments are ignored
    NUMBER: /\d+/
    PLUS: /\+/
    %skip /[ \t]+/
    """
    definition = parser.parse(dsl)

    assert len(definition.tokens) == 2
    assert definition.tokens[0] == ("NUMBER", r"\d+", 0)
    assert definition.tokens[1] == ("PLUS", r"\+", 0)
    assert len(definition.skips) == 1
    assert definition.skips[0] == r"[ \t]+"

def test_parse_trailing_comment():
    parser = DSLParser()
    dsl = r"NUMBER: /\d+/ # this is a comment"
    definition = parser.parse(dsl)
    assert len(definition.tokens) == 1
    assert definition.tokens[0] == ("NUMBER", r"\d+", 0)

def test_parse_priority():
    parser = DSLParser()
    dsl = "IF: /if/ 10"
    definition = parser.parse(dsl)

    assert definition.tokens[0] == ("IF", "if", 10)

def test_parse_multiple_skips():
    parser = DSLParser()
    dsl = r"""
    %skip /[ \t]+/
    %skip /#.*/
    """
    definition = parser.parse(dsl)

    assert len(definition.skips) == 2
    assert definition.skips[0] == r"[ \t]+"
    assert definition.skips[1] == r"#.*"

def test_parse_invalid_syntax():
    parser = DSLParser()
    with pytest.raises(DSLParserError):
        parser.parse("INVALID LINE")

def test_parse_invalid_token_name():
    parser = DSLParser()
    with pytest.raises(DSLParserError):
        parser.parse("lower_case: /abc/")

def test_empty_dsl():
    parser = DSLParser()
    definition = parser.parse("")
    assert len(definition.tokens) == 0
    assert len(definition.skips) == 0
