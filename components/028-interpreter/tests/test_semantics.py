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

def test_boolean_literal_type():
    source = "let t = true let f = false"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert isinstance(evaluator.globals.get("t"), BooleanValue)
    assert isinstance(evaluator.globals.get("f"), BooleanValue)
    assert not isinstance(evaluator.globals.get("t"), IntegerValue)

def test_float_truthiness():
    source = "let res = 0 if 0.5 { res = 1 } else { res = 2 } let res2 = 0 if 0.0 { res2 = 1 } else { res2 = 2 }"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    assert evaluator.globals.get("res") == IntegerValue(1)
    assert evaluator.globals.get("res2") == IntegerValue(2)

def test_modulo_precision():
    source = "let r = 5.5 % 2.0"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    res = evaluator.globals.get("r")
    assert isinstance(res, FloatValue)
    assert res.value == 1.5

def test_type_aware_equality():
    source = "let a = (1 == true) let b = (0 == false) let c = (1 == 1)"
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)

    # 1 == true should be false in our language, because they are different types
    assert evaluator.globals.get("a") == BooleanValue(False)
    assert evaluator.globals.get("b") == BooleanValue(False)
    assert evaluator.globals.get("c") == BooleanValue(True)
