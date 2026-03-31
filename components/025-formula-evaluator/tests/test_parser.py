import pytest
from src.formula.lexer import Lexer, TokenType
from src.formula.parser import Parser, NumberNode, BinaryOpNode, FunctionCallNode, CellNode

def test_lexer_simple():
    lexer = Lexer("1+2*3")
    tokens = lexer.tokenize()
    assert len(tokens) == 5
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[1].type == TokenType.OPERATOR
    assert tokens[2].type == TokenType.NUMBER
    assert tokens[3].type == TokenType.OPERATOR
    assert tokens[4].type == TokenType.NUMBER

def test_lexer_complex():
    lexer = Lexer("SUM(A1, B2:C3, \"hello\")")
    tokens = lexer.tokenize()
    # SUM, (, A1, ,, B2:C3, ,, "hello", )
    assert tokens[0].type == TokenType.FUNCTION
    assert tokens[1].type == TokenType.LPAREN
    assert tokens[2].type == TokenType.CELL
    assert tokens[3].type == TokenType.COMMA
    assert tokens[4].type == TokenType.RANGE
    assert tokens[5].type == TokenType.COMMA
    assert tokens[6].type == TokenType.STRING
    assert tokens[7].type == TokenType.RPAREN

def test_parser_simple():
    lexer = Lexer("1+2")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assert isinstance(ast, BinaryOpNode)
    assert ast.op == "+"
    assert ast.left.value == 1.0
    assert ast.right.value == 2.0

def test_parser_precedence():
    lexer = Lexer("1+2*3")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assert isinstance(ast, BinaryOpNode)
    assert ast.op == "+"
    assert isinstance(ast.right, BinaryOpNode)
    assert ast.right.op == "*"

def test_parser_function():
    lexer = Lexer("SUM(1, 2)")
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assert isinstance(ast, FunctionCallNode)
    assert ast.name == "SUM"
    assert len(ast.args) == 2
