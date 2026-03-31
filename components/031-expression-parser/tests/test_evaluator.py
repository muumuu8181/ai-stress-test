import math

import pytest

from src.ast_nodes import (AssignmentNode, BinaryOpNode, FunctionCallNode,
                           NumberNode, TokenType, VariableNode)
from src.evaluator import Environment, Evaluator


def test_eval_simple():
    evaluator = Evaluator()
    # 1 + 2
    ast = BinaryOpNode(NumberNode(1), TokenType.PLUS, NumberNode(2))
    assert evaluator.evaluate(ast) == 3.0


def test_eval_division_by_zero():
    evaluator = Evaluator()
    # 1 / 0
    ast = BinaryOpNode(NumberNode(1), TokenType.DIVIDE, NumberNode(0))
    with pytest.raises(ZeroDivisionError):
        evaluator.evaluate(ast)


def test_eval_environment():
    env = Environment()
    evaluator = Evaluator(env)
    # x = 10
    ast_assign = AssignmentNode("x", NumberNode(10))
    assert evaluator.evaluate(ast_assign) == 10.0
    assert env.get("x") == 10.0

    # x * 2
    ast_var = BinaryOpNode(
        VariableNode("x"), TokenType.MULTIPLY, NumberNode(2)
    )
    assert evaluator.evaluate(ast_var) == 20.0


def test_eval_undefined_variable():
    evaluator = Evaluator()
    ast = VariableNode("y")
    with pytest.raises(LookupError, match="Undefined variable: y"):
        evaluator.evaluate(ast)


def test_eval_function():
    evaluator = Evaluator()
    # sin(0)
    ast = FunctionCallNode("sin", [NumberNode(0)])
    assert evaluator.evaluate(ast) == 0.0

    # cos(0)
    ast_cos = FunctionCallNode("cos", [NumberNode(0)])
    assert evaluator.evaluate(ast_cos) == 1.0


def test_eval_undefined_function():
    evaluator = Evaluator()
    ast = FunctionCallNode("unknown", [])
    with pytest.raises(ValueError, match="Undefined function: unknown"):
        evaluator.evaluate(ast)
