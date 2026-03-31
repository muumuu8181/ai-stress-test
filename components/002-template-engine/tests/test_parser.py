import pytest
from templateengine.lexer import Lexer
from templateengine.parser import Parser
from templateengine.nodes import (
    TextNode, VariableNode, IfNode, ForNode, ExtendsNode, BlockNode
)

def test_parse_text():
    lexer = Lexer("Simple text")
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    assert len(ast.children) == 1
    assert isinstance(ast.children[0], TextNode)
    assert ast.children[0].text == "Simple text"

def test_parse_variable():
    lexer = Lexer("{{ name }}")
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    assert len(ast.children) == 1
    assert isinstance(ast.children[0], VariableNode)
    assert ast.children[0].expression == "name"

def test_parse_if():
    lexer = Lexer("{% if condition %}True{% else %}False{% endif %}")
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    assert len(ast.children) == 1
    if_node = ast.children[0]
    assert isinstance(if_node, IfNode)
    assert if_node.condition == "condition"
    assert len(if_node.then_nodes) == 1
    assert isinstance(if_node.then_nodes[0], TextNode)
    assert if_node.then_nodes[0].text == "True"
    assert len(if_node.else_nodes) == 1
    assert isinstance(if_node.else_nodes[0], TextNode)
    assert if_node.else_nodes[0].text == "False"

def test_parse_elif():
    lexer = Lexer("{% if a %}1{% elif b %}2{% else %}3{% endif %}")
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    if_node = ast.children[0]
    assert len(if_node.elif_nodes) == 1
    assert if_node.elif_nodes[0][0] == "b"
    assert if_node.elif_nodes[0][1][0].text == "2"

def test_parse_for():
    lexer = Lexer("{% for item in items %}{{ item }}{% endfor %}")
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    assert len(ast.children) == 1
    for_node = ast.children[0]
    assert isinstance(for_node, ForNode)
    assert for_node.item_name == "item"
    assert for_node.collection_expr == "items"
    assert len(for_node.body_nodes) == 1
    assert isinstance(for_node.body_nodes[0], VariableNode)

def test_parse_extends_and_blocks():
    template = '{% extends "base.html" %}{% block content %}Hello{% endblock %}'
    lexer = Lexer(template)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    assert len(ast.children) == 2
    assert isinstance(ast.children[0], ExtendsNode)
    assert ast.children[0].parent_template == "base.html"
    assert isinstance(ast.children[1], BlockNode)
    assert ast.children[1].name == "content"
    assert ast.children[1].body_nodes[0].text == "Hello"

def test_parse_invalid_syntax():
    with pytest.raises(SyntaxError) as exc:
        Parser(Lexer("{% if %}").tokenize()).parse()
    assert "Unknown tag" not in str(exc.value) # It should be empty block or similar

    with pytest.raises(SyntaxError):
        Parser(Lexer("{% for x %}").tokenize()).parse()
