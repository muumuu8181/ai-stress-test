import pytest
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "components/028-interpreter/src"))

from interpreter.lexer import Lexer
from interpreter.parser import (
    Parser, LetStmt, LiteralExpr, BinaryExpr, IfStmt, WhileStmt, ForStmt, FunctionStmt
)

def test_parser_let_stmt():
    source = "let x = 10"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    assert len(statements) == 1
    assert isinstance(statements[0], LetStmt)
    assert statements[0].name.lexeme == "x"
    assert isinstance(statements[0].initializer, LiteralExpr)
    assert statements[0].initializer.value == 10

def test_parser_binary_expression():
    source = "1 + 2 * 3"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    # 1 + (2 * 3)
    expr = statements[0].expression
    assert isinstance(expr, BinaryExpr)
    assert expr.operator.lexeme == "+"
    assert isinstance(expr.right, BinaryExpr)
    assert expr.right.operator.lexeme == "*"

def test_parser_if_statement():
    source = "if true { 1 } elif false { 2 } else { 3 }"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    assert isinstance(statements[0], IfStmt)
    assert len(statements[0].elif_branches) == 1
    assert statements[0].else_branch is not None

def test_parser_while_statement():
    source = "while true { 1 }"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    assert isinstance(statements[0], WhileStmt)

def test_parser_for_statement():
    source = "for i in [1, 2] { 1 }"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    assert isinstance(statements[0], ForStmt)
    assert statements[0].item.lexeme == "i"

def test_parser_function_declaration():
    source = "fn add(a, b) { a + b }"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    assert isinstance(statements[0], FunctionStmt)
    assert statements[0].name.lexeme == "add"
    assert len(statements[0].params) == 2

def test_parser_error():
    source = "let x ="
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    with pytest.raises(SyntaxError):
        parser.parse()
