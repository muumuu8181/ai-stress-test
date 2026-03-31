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

def test_builtin_print(capsys):
    source = "print(10, 'hello')"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    captured = capsys.readouterr()
    assert captured.out.strip() == "10 hello"

def test_builtin_len():
    source = "let a = len([1, 2, 3]) let s = len('hello')"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("a") == IntegerValue(3)
    assert evaluator.globals.get("s") == IntegerValue(5)

def test_builtin_type():
    source = "let a = type(10) let b = type('hi') let c = type([1])"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("a") == StringValue("integer")
    assert evaluator.globals.get("b") == StringValue("string")
    assert evaluator.globals.get("c") == StringValue("array")

def test_builtin_push_pop():
    source = "let a = [1, 2] push(a, 3) let x = pop(a)"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("a") == ArrayValue([IntegerValue(1), IntegerValue(2)])
    assert evaluator.globals.get("x") == IntegerValue(3)

def test_function_call():
    source = "let x = 0 fn set_x(v) { x = v } set_x(10)"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("x") == IntegerValue(10)

def test_function_multiple_params():
    source = """
    let res = 0
    fn add(a, b, c) {
      res = a + b + c
    }
    add(1, 2, 3)
    """
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("res") == IntegerValue(6)
