from typing import Any, List, Optional, Union
from .lexer import Token, TokenType
from .parser import (
    Expr, BinaryExpr, UnaryExpr, LiteralExpr, GroupingExpr,
    VariableExpr, AssignExpr, ArrayExpr, IndexExpr, CallExpr, LogicalExpr,
    Stmt, ExpressionStmt, LetStmt, BlockStmt, IfStmt, WhileStmt, ForStmt, FunctionStmt
)
from .types import (
    Value, IntegerValue, FloatValue, StringValue, BooleanValue,
    ArrayValue, FunctionValue, BuiltinFunctionValue
)
from .environment import Environment
from .builtins import get_builtins

class Evaluator:
    """Class to evaluate statements and expressions from the AST."""
    def __init__(self):
        self.globals = Environment()
        for b in get_builtins():
            self.globals.define(b.name, b)
        self.environment = self.globals

    def interpret(self, statements: List[Stmt]):
        """Evaluates a list of statements."""
        for stmt in statements:
            self.execute(stmt)

    def execute(self, stmt: Stmt):
        """Executes a single statement."""
        if isinstance(stmt, ExpressionStmt):
            self.evaluate(stmt.expression)
        elif isinstance(stmt, LetStmt):
            value = self.evaluate(stmt.initializer)
            self.environment.define(stmt.name.lexeme, value)
        elif isinstance(stmt, BlockStmt):
            self.execute_block(stmt.statements, Environment(self.environment))
        elif isinstance(stmt, IfStmt):
            self.execute_if(stmt)
        elif isinstance(stmt, WhileStmt):
            while self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.body)
        elif isinstance(stmt, ForStmt):
            self.execute_for(stmt)
        elif isinstance(stmt, FunctionStmt):
            func = FunctionValue(stmt.name.lexeme, [p.lexeme for p in stmt.params], stmt.body, self.environment)
            self.environment.define(stmt.name.lexeme, func)
        else:
            raise TypeError(f"Unknown statement type: {type(stmt)}")

    def execute_block(self, statements: List[Stmt], environment: Environment):
        """Executes a block of statements in a new environment."""
        previous = self.environment
        try:
            self.environment = environment
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def execute_if(self, stmt: IfStmt):
        """Executes an if-elif-else statement."""
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
            return

        for elif_cond, elif_body in stmt.elif_branches:
            if self.is_truthy(self.evaluate(elif_cond)):
                self.execute(elif_body)
                return

        if stmt.else_branch:
            self.execute(stmt.else_branch)

    def execute_for(self, stmt: ForStmt):
        """Executes a for-in loop."""
        iterable = self.evaluate(stmt.iterable)
        if not isinstance(iterable, (ArrayValue, StringValue)):
            raise TypeError("Iterable must be an array or string.")

        items = []
        if isinstance(iterable, ArrayValue):
            items = iterable.value
        else:
            items = [StringValue(c) for c in iterable.value]

        for item in items:
            inner_env = Environment(self.environment)
            inner_env.define(stmt.item.lexeme, item)
            self.execute_block([stmt.body], inner_env)

    def evaluate(self, expr: Expr) -> Value:
        """Evaluates an expression and returns a runtime Value."""
        if isinstance(expr, LiteralExpr):
            # Swap bool/int checks to avoid bool being caught by int (since bool is a subclass of int in Python)
            if isinstance(expr.value, bool): return BooleanValue(expr.value)
            if isinstance(expr.value, int): return IntegerValue(expr.value)
            if isinstance(expr.value, float): return FloatValue(expr.value)
            if isinstance(expr.value, str): return StringValue(expr.value)
            return Value(expr.value)
        elif isinstance(expr, GroupingExpr):
            return self.evaluate(expr.expression)
        elif isinstance(expr, UnaryExpr):
            return self.evaluate_unary(expr)
        elif isinstance(expr, BinaryExpr):
            return self.evaluate_binary(expr)
        elif isinstance(expr, VariableExpr):
            return self.environment.get(expr.name.lexeme)
        elif isinstance(expr, AssignExpr):
            value = self.evaluate(expr.value)
            self.environment.assign(expr.name.lexeme, value)
            return value
        elif isinstance(expr, LogicalExpr):
            return self.evaluate_logical(expr)
        elif isinstance(expr, ArrayExpr):
            return ArrayValue([self.evaluate(e) for e in expr.elements])
        elif isinstance(expr, IndexExpr):
            return self.evaluate_index(expr)
        elif isinstance(expr, CallExpr):
            return self.evaluate_call(expr)
        else:
            raise TypeError(f"Unknown expression type: {type(expr)}")

    def evaluate_unary(self, expr: UnaryExpr) -> Value:
        """Evaluates a unary expression."""
        right = self.evaluate(expr.right)
        op_type = expr.operator.type

        if op_type == TokenType.MINUS:
            if isinstance(right, IntegerValue): return IntegerValue(-right.value)
            if isinstance(right, FloatValue): return FloatValue(-right.value)
            raise TypeError("Unary '-' operand must be a number.")
        if op_type == TokenType.NOT:
            return BooleanValue(not self.is_truthy(right))

        raise TypeError(f"Unknown unary operator: {op_type}")

    def evaluate_binary(self, expr: BinaryExpr) -> Value:
        """Evaluates a binary expression."""
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        op_type = expr.operator.type

        # Arithmetic
        if op_type == TokenType.PLUS:
            if isinstance(left, IntegerValue) and isinstance(right, IntegerValue):
                return IntegerValue(left.value + right.value)
            if isinstance(left, (IntegerValue, FloatValue)) and isinstance(right, (IntegerValue, FloatValue)):
                return FloatValue(float(left.value) + float(right.value))
            if isinstance(left, StringValue) and isinstance(right, StringValue):
                return StringValue(left.value + right.value)
            raise TypeError("Operands of '+' must be numbers or strings.")

        if op_type == TokenType.MINUS:
            if isinstance(left, (IntegerValue, FloatValue)) and isinstance(right, (IntegerValue, FloatValue)):
                res = left.value - right.value
                return IntegerValue(res) if isinstance(left, IntegerValue) and isinstance(right, IntegerValue) else FloatValue(float(res))
            raise TypeError("Operands of '-' must be numbers.")

        if op_type == TokenType.STAR:
            if isinstance(left, (IntegerValue, FloatValue)) and isinstance(right, (IntegerValue, FloatValue)):
                res = left.value * right.value
                return IntegerValue(res) if isinstance(left, IntegerValue) and isinstance(right, IntegerValue) else FloatValue(float(res))
            raise TypeError("Operands of '*' must be numbers.")

        if op_type == TokenType.SLASH:
            if isinstance(left, (IntegerValue, FloatValue)) and isinstance(right, (IntegerValue, FloatValue)):
                if right.value == 0: raise ZeroDivisionError("Division by zero.")
                res = left.value / right.value
                return IntegerValue(int(res)) if isinstance(left, IntegerValue) and isinstance(right, IntegerValue) and res == int(res) else FloatValue(float(res))
            raise TypeError("Operands of '/' must be numbers.")

        if op_type == TokenType.PERCENT:
            if isinstance(left, (IntegerValue, FloatValue)) and isinstance(right, (IntegerValue, FloatValue)):
                res = left.value % right.value
                return IntegerValue(int(res)) if isinstance(left, IntegerValue) and isinstance(right, IntegerValue) else FloatValue(float(res))
            raise TypeError("Operands of '%' must be numbers.")

        # Comparison
        if op_type == TokenType.GREATER:
            return BooleanValue(left.value > right.value)
        if op_type == TokenType.GREATER_EQUAL:
            return BooleanValue(left.value >= right.value)
        if op_type == TokenType.LESS:
            return BooleanValue(left.value < right.value)
        if op_type == TokenType.LESS_EQUAL:
            return BooleanValue(left.value <= right.value)
        if op_type == TokenType.BANG_EQUAL:
            return BooleanValue(left != right) # Use Value.__eq__ which is now type-aware
        if op_type == TokenType.EQUAL_EQUAL:
            return BooleanValue(left == right) # Use Value.__eq__ which is now type-aware

        raise TypeError(f"Unknown binary operator: {op_type}")

    def evaluate_logical(self, expr: LogicalExpr) -> Value:
        """Evaluates a logical AND/OR expression."""
        left = self.evaluate(expr.left)
        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left): return left
        else:
            if not self.is_truthy(left): return left
        return self.evaluate(expr.right)

    def evaluate_index(self, expr: IndexExpr) -> Value:
        """Evaluates an array index access."""
        array = self.evaluate(expr.array)
        index = self.evaluate(expr.index)

        if not isinstance(array, (ArrayValue, StringValue)):
            raise TypeError("Index access only supported for arrays and strings.")
        if not isinstance(index, IntegerValue):
            raise TypeError("Index must be an integer.")

        try:
            val = array.value[index.value]
            if isinstance(array, StringValue): return StringValue(val)
            return val
        except IndexError:
            raise IndexError("Index out of range.")

    def evaluate_call(self, expr: CallExpr) -> Value:
        """Evaluates a function call."""
        callee = self.evaluate(expr.callee)
        arguments = [self.evaluate(arg) for arg in expr.arguments]

        if isinstance(callee, BuiltinFunctionValue):
            return callee.func(arguments)

        if isinstance(callee, FunctionValue):
            if len(arguments) != len(callee.params):
                raise ValueError(f"Expected {len(callee.params)} arguments but got {len(arguments)}.")

            environment = Environment(callee.env)
            for i, param in enumerate(callee.params):
                environment.define(param, arguments[i])

            self.execute_block(callee.body, environment)
            return BooleanValue(True)

        raise TypeError("Object not callable.")

    def is_truthy(self, val: Value) -> bool:
        """Determines if a Value is truthy."""
        if isinstance(val, BooleanValue): return val.value
        if isinstance(val, IntegerValue): return val.value != 0
        if isinstance(val, FloatValue): return val.value != 0.0
        if isinstance(val, StringValue): return len(val.value) > 0
        if isinstance(val, ArrayValue): return len(val.value) > 0
        return False
