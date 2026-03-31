import math

import pytest

from src.evaluator import Environment, Evaluator
from src.parser import Parser


def test_integration_arithmetic():
    parser = Parser("1 + 2 * (3 - 4) / 5")
    ast = parser.parse()
    evaluator = Evaluator()
    # 1 + 2 * (-1) / 5 = 1 - 0.4 = 0.6
    assert evaluator.evaluate(ast) == pytest.approx(0.6)


def test_integration_assignment_and_use():
    env = Environment()
    evaluator = Evaluator(env)

    # x = 10
    ast1 = Parser("x = 10").parse()
    evaluator.evaluate(ast1)

    # y = x * 2
    ast2 = Parser("y = x * 2").parse()
    evaluator.evaluate(ast2)

    # y + 5
    ast3 = Parser("y + 5").parse()
    result = evaluator.evaluate(ast3)

    assert result == 25.0
    assert env.get("x") == 10.0
    assert env.get("y") == 20.0


def test_integration_functions():
    evaluator = Evaluator()

    # sin(pi/2)
    # Since pi is not predefined, let's just use a number or define it
    env = Environment()
    env.set("pi", math.pi)
    evaluator = Evaluator(env)

    ast = Parser("sin(pi / 2)").parse()
    assert evaluator.evaluate(ast) == pytest.approx(1.0)

    ast_log = Parser("log(10, 10)").parse()  # log(x, base)
    assert evaluator.evaluate(ast_log) == pytest.approx(1.0)


def test_integration_complex_expression():
    env = Environment()
    evaluator = Evaluator(env)

    # a = 5, b = 2
    evaluator.evaluate(Parser("a = 5").parse())
    evaluator.evaluate(Parser("b = 2").parse())

    # c = sqrt(a*a + b*b)
    ast = Parser("c = sqrt(a*a + b*b)").parse()
    result = evaluator.evaluate(ast)

    assert result == pytest.approx(math.sqrt(5 * 5 + 2 * 2))
    assert env.get("c") == result


def test_edge_case_empty_input():
    # If I pass empty string to Parser, Lexer will return EOF.
    # Parser should probably handle it or throw an error.
    # Currently my Parser.parse calls self.expression() which calls sum() -> term() -> factor() -> primary().
    # primary() will raise SyntaxError for EOF.
    with pytest.raises(SyntaxError):
        Parser("").parse()


def test_edge_case_only_spaces():
    with pytest.raises(SyntaxError):
        Parser("   ").parse()


def test_edge_case_invalid_syntax():
    with pytest.raises(SyntaxError):
        Parser("1 + * 2").parse()


def test_edge_case_nested_functions():
    evaluator = Evaluator()
    ast = Parser("sin(cos(0))").parse()
    # sin(cos(0)) = sin(1)
    assert evaluator.evaluate(ast) == pytest.approx(math.sin(1.0))
