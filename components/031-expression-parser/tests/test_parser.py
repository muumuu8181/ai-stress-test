import pytest

from src.ast_nodes import (AssignmentNode, BinaryOpNode, FunctionCallNode,
                           NumberNode, TokenType, UnaryOpNode, VariableNode)
from src.parser import Parser


def test_parser_simple():
    parser = Parser("1 + 2")
    ast = parser.parse()
    assert isinstance(ast, BinaryOpNode)
    assert ast.op == TokenType.PLUS
    assert isinstance(ast.left, NumberNode)
    assert ast.right.value == 2.0


def test_parser_precedence():
    parser = Parser("1 + 2 * 3")
    ast = parser.parse()
    # 1 + (2 * 3)
    assert isinstance(ast, BinaryOpNode)
    assert ast.op == TokenType.PLUS
    assert isinstance(ast.right, BinaryOpNode)
    assert ast.right.op == TokenType.MULTIPLY


def test_parser_parentheses():
    parser = Parser("(1 + 2) * 3")
    ast = parser.parse()
    # (1 + 2) * 3
    assert isinstance(ast, BinaryOpNode)
    assert ast.op == TokenType.MULTIPLY
    assert isinstance(ast.left, BinaryOpNode)
    assert ast.left.op == TokenType.PLUS


def test_parser_assignment():
    parser = Parser("x = 10")
    ast = parser.parse()
    assert isinstance(ast, AssignmentNode)
    assert ast.name == "x"
    assert isinstance(ast.expr, NumberNode)


def test_parser_function_call():
    parser = Parser("sin(1, 2)")
    ast = parser.parse()
    assert isinstance(ast, FunctionCallNode)
    assert ast.name == "sin"
    assert len(ast.args) == 2


def test_parser_unary():
    parser = Parser("-5")
    ast = parser.parse()
    assert isinstance(ast, UnaryOpNode)
    assert ast.op == TokenType.MINUS
    assert ast.expr.value == 5.0


def test_parser_error():
    parser = Parser("1 + ")
    with pytest.raises(SyntaxError):
        parser.parse()
