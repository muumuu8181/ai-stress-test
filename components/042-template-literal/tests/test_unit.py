import pytest
from templateliteral.lexer import Lexer, TokenType
from templateliteral.parser import Parser, TemplateSyntaxError
from templateliteral.nodes import RootNode, TextNode, ExpressionNode, IfNode, EachNode

def test_lexer_basic():
    template = "Hello, ${name}!"
    lexer = Lexer(template)
    tokens = lexer.tokenize()

    assert tokens[0].type == TokenType.TEXT
    assert tokens[0].value == "Hello, "
    assert tokens[1].type == TokenType.EXPR_START
    assert tokens[2].type == TokenType.TEXT
    assert tokens[2].value == "name"
    assert tokens[3].type == TokenType.EXPR_END
    assert tokens[4].type == TokenType.TEXT
    assert tokens[4].value == "!"

def test_lexer_line_numbers():
    template = "Line 1\nLine 2 ${expr}"
    lexer = Lexer(template)
    tokens = lexer.tokenize()

    # "Line 1\nLine 2 "
    assert tokens[0].line == 1
    assert tokens[1].line == 2 # ${
    assert tokens[2].line == 2 # expr

def test_lexer_if_each():
    template = "{?condition}Each: {@each items as i}${i}{/each}{/?}"
    lexer = Lexer(template)
    tokens = lexer.tokenize()

    types = [t.type for t in tokens]
    assert TokenType.IF_START in types
    assert TokenType.EACH_START in types
    assert TokenType.END_EACH in types
    assert TokenType.END_IF in types

def test_lexer_unclosed():
    with pytest.raises(SyntaxError):
        Lexer("${expr").tokenize()
    with pytest.raises(SyntaxError):
        Lexer("{?cond").tokenize()
    with pytest.raises(SyntaxError):
        Lexer("{@each x").tokenize()

def test_parser_basic():
    template = "Hello, ${name}!"
    lexer = Lexer(template)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    assert isinstance(ast, RootNode)
    assert len(ast.children) == 3
    assert isinstance(ast.children[0], TextNode)
    assert isinstance(ast.children[1], ExpressionNode)
    assert isinstance(ast.children[2], TextNode)

def test_parser_nested():
    template = "{?a}{@each items as i}${i}{/each}{/?}"
    lexer = Lexer(template)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    assert len(ast.children) == 1
    if_node = ast.children[0]
    assert isinstance(if_node, IfNode)
    assert len(if_node.body) == 1
    each_node = if_node.body[0]
    assert isinstance(each_node, EachNode)

def test_parser_invalid_each():
    template = "{@each items}bad{/each}"
    lexer = Lexer(template)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    with pytest.raises(TemplateSyntaxError) as excinfo:
        parser.parse()
    assert "Invalid @each syntax" in str(excinfo.value)

def test_parser_unexpected_token():
    template = "{/?}"
    lexer = Lexer(template)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    with pytest.raises(TemplateSyntaxError) as excinfo:
        parser.parse()
    assert "Unexpected token END_IF" in str(excinfo.value)
