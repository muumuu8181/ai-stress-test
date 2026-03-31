import math
from typing import Callable, Dict, Optional

from .ast_nodes import (AssignmentNode, ASTNode, BinaryOpNode,
                        FunctionCallNode, NumberNode, TokenType, UnaryOpNode,
                        VariableNode)


class Environment:
    """Manages variables and their values."""

    def __init__(self, parent: Optional["Environment"] = None) -> None:
        """
        Initialize the environment.

        Args:
            parent (Environment, optional): The parent environment.
        """
        self.variables: Dict[str, float] = {}
        self.parent = parent

    def set(self, name: str, value: float) -> None:
        """
        Assign a value to a variable.

        Args:
            name (str): The variable name.
            value (float): The variable value.
        """
        self.variables[name] = value

    def get(self, name: str) -> float:
        """
        Get the value of a variable.

        Args:
            name (str): The variable name.

        Returns:
            float: The variable value.

        Raises:
            LookupError: If the variable is not found.
        """
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise LookupError(f"Undefined variable: {name}")


class Evaluator:
    """Evaluates the AST produced by the parser."""

    def __init__(self, env: Optional[Environment] = None) -> None:
        """
        Initialize the evaluator.

        Args:
            env (Environment, optional): The environment to use.
        """
        self.env = env if env else Environment()
        self.functions: Dict[str, Callable[..., float]] = {
            "sin": math.sin,
            "cos": math.cos,
            "log": math.log,
            "tan": math.tan,
            "sqrt": math.sqrt,
            "abs": abs,
            "exp": math.exp,
        }

    def evaluate(self, node: ASTNode) -> float:
        """
        Recursively evaluate an AST node.

        Args:
            node (ASTNode): The root node of the AST.

        Returns:
            float: The result of the evaluation.

        Raises:
            ValueError: For invalid operations.
        """
        if isinstance(node, NumberNode):
            return node.value

        if isinstance(node, BinaryOpNode):
            left_val = self.evaluate(node.left)
            right_val = self.evaluate(node.right)
            if node.op == TokenType.PLUS:
                return left_val + right_val
            if node.op == TokenType.MINUS:
                return left_val - right_val
            if node.op == TokenType.MULTIPLY:
                return left_val * right_val
            if node.op == TokenType.DIVIDE:
                if right_val == 0:
                    raise ZeroDivisionError("Division by zero")
                return left_val / right_val

        if isinstance(node, UnaryOpNode):
            val = self.evaluate(node.expr)
            if node.op == TokenType.PLUS:
                return +val
            if node.op == TokenType.MINUS:
                return -val

        if isinstance(node, VariableNode):
            return self.env.get(node.name)

        if isinstance(node, AssignmentNode):
            val = self.evaluate(node.expr)
            self.env.set(node.name, val)
            return val

        if isinstance(node, FunctionCallNode):
            if node.name not in self.functions:
                raise ValueError(f"Undefined function: {node.name}")
            args = [self.evaluate(arg) for arg in node.args]
            return self.functions[node.name](*args)

        raise ValueError(f"Unknown AST node: {type(node)}")
