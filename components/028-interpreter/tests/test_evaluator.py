import pytest
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "components/028-interpreter/src"))

from interpreter.lexer import Lexer
from interpreter.parser import Parser
from interpreter.evaluator import Evaluator
from interpreter.types import (
    IntegerValue, FloatValue, StringValue, BooleanValue, ArrayValue
)

def test_evaluator_literals():
    source = "let x = 10 let y = 3.14 let s = 'hello' let b = true let a = [1, 2]"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("x") == IntegerValue(10)
    assert evaluator.globals.get("y") == FloatValue(3.14)
    assert evaluator.globals.get("s") == StringValue("hello")
    assert evaluator.globals.get("b") == BooleanValue(True)
    assert evaluator.globals.get("a") == ArrayValue([IntegerValue(1), IntegerValue(2)])

def test_evaluator_arithmetic():
    source = "let x = 10 + 2 * 3 - 4 / 2 let y = 10 % 3"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("x") == IntegerValue(14)
    assert evaluator.globals.get("y") == IntegerValue(1)

def test_evaluator_string_concatenation():
    source = "let s = 'hello' + ' world'"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("s") == StringValue("hello world")

def test_evaluator_logical():
    source = "let a = true and false let b = true or false let c = not true"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("a") == BooleanValue(False)
    assert evaluator.globals.get("b") == BooleanValue(True)
    assert evaluator.globals.get("c") == BooleanValue(False)

def test_evaluator_comparison():
    source = "let a = 10 > 5 let b = 10 < 5 let c = 10 == 10 let d = 10 != 5"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("a") == BooleanValue(True)
    assert evaluator.globals.get("b") == BooleanValue(False)
    assert evaluator.globals.get("c") == BooleanValue(True)
    assert evaluator.globals.get("d") == BooleanValue(True)

def test_evaluator_if():
    source = "let x = 0 if true { x = 1 } else { x = 2 } let y = 0 if false { y = 1 } else { y = 2 }"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("x") == IntegerValue(1)
    assert evaluator.globals.get("y") == IntegerValue(2)

def test_evaluator_while():
    source = "let x = 0 while x < 5 { x = x + 1 }"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("x") == IntegerValue(5)

def test_evaluator_for():
    source = "let sum = 0 for i in [1, 2, 3, 4] { sum = sum + i }"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("sum") == IntegerValue(10)

def test_evaluator_array_index():
    source = "let a = [10, 20] let x = a[0] let y = a[1]"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("x") == IntegerValue(10)
    assert evaluator.globals.get("y") == IntegerValue(20)

def test_evaluator_string_index():
    source = "let s = 'hello' let x = s[0]"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("x") == StringValue("h")
