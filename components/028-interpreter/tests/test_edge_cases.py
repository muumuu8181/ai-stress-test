import pytest
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "components/028-interpreter/src"))

from interpreter.lexer import Lexer
from interpreter.parser import Parser
from interpreter.evaluator import Evaluator
from interpreter.types import (
    IntegerValue, StringValue, ArrayValue, BooleanValue
)

def test_empty_input():
    source = ""
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert len(evaluator.globals.values) == 5 # built-ins only

def test_division_by_zero():
    source = "let x = 10 / 0"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    with pytest.raises(ZeroDivisionError):
        evaluator.interpret(statements)

def test_invalid_index():
    source = "let a = [1, 2] let x = a[2]"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    with pytest.raises(IndexError):
        evaluator.interpret(statements)

def test_undefined_variable():
    source = "let x = y"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    with pytest.raises(NameError):
        evaluator.interpret(statements)

def test_type_error_arithmetic():
    source = "let x = 10 + 'hello'"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    with pytest.raises(TypeError):
        evaluator.interpret(statements)

def test_function_wrong_args():
    source = "fn add(a, b) { a + b } add(1)"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    with pytest.raises(ValueError):
        evaluator.interpret(statements)
