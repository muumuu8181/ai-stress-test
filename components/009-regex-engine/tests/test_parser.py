import pytest
from regexengine.lexer import Lexer
from regexengine.parser import Parser, LiteralNode, ConcatenationNode, AlternationNode, QuantifierNode, GroupNode, CharClassNode

def test_parser_simple():
    tokens = Lexer("ab").tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assert isinstance(ast, ConcatenationNode)
    assert len(ast.nodes) == 2
    assert isinstance(ast.nodes[0], LiteralNode)
    assert ast.nodes[0].char == 'a'

def test_parser_alternation():
    tokens = Lexer("a|b").tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assert isinstance(ast, AlternationNode)
    assert len(ast.nodes) == 2
    assert isinstance(ast.nodes[0], LiteralNode)
    assert ast.nodes[0].char == 'a'

def test_parser_quantifier():
    tokens = Lexer("a*").tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assert isinstance(ast, QuantifierNode)
    assert ast.min_count == 0
    assert ast.max_count is None
    assert isinstance(ast.node, LiteralNode)

def test_parser_group():
    tokens = Lexer("(a)").tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assert isinstance(ast, GroupNode)
    assert ast.group_index == 1
    assert isinstance(ast.node, LiteralNode)

def test_parser_char_class():
    tokens = Lexer("[a-z]").tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assert isinstance(ast, CharClassNode)
    assert len(ast.ranges) == 1
    assert ast.ranges[0] == ('a', 'z')

def test_parser_brace():
    tokens = Lexer("a{2,3}").tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assert isinstance(ast, QuantifierNode)
    assert ast.min_count == 2
    assert ast.max_count == 3

def test_parser_error():
    tokens = Lexer("(a").tokenize()
    parser = Parser(tokens)
    with pytest.raises(ValueError):
        parser.parse()
