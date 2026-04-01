import re
import ast
import html
from typing import Any, Dict, List, Optional, Callable, Union, Type
from .lexer import Lexer
from .parser import Parser, TemplateSyntaxError
from .nodes import Node, RootNode, TextNode, ExpressionNode, IfNode, EachNode
from .filters import DEFAULT_FILTERS, escape_html, SafeString

class SafeEvaluator(ast.NodeVisitor):
    """
    A safe expression evaluator that visits an AST tree and evaluates it
    within a restricted set of allowed operations.
    """
    ALLOWED_OPERATORS = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.FloorDiv: lambda a, b: a // b,
        ast.Mod: lambda a, b: a % b,
        ast.Pow: lambda a, b: a ** b,
        ast.USub: lambda a: -a,
        ast.UAdd: lambda a: +a,
        ast.Not: lambda a: not a,
        ast.And: lambda a, b: a and b,
        ast.Or: lambda a, b: a or b,
        ast.Eq: lambda a, b: a == b,
        ast.NotEq: lambda a, b: a != b,
        ast.Lt: lambda a, b: a < b,
        ast.LtE: lambda a, b: a <= b,
        ast.Gt: lambda a, b: a > b,
        ast.GtE: lambda a, b: a >= b,
        ast.In: lambda a, b: a in b,
        ast.NotIn: lambda a, b: a not in b,
    }

    def __init__(self, context: Dict[str, Any]):
        self.context = context

    def evaluate(self, node: ast.AST) -> Any:
        return self.visit(node)

    def visit_Expression(self, node: ast.Expression) -> Any:
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant) -> Any:
        return node.value

    def visit_Name(self, node: ast.Name) -> Any:
        if isinstance(node.ctx, ast.Load):
            if node.id in self.context:
                return self.context[node.id]
            # Handle common built-ins or literals if not in context
            if node.id == "True": return True
            if node.id == "False": return False
            if node.id == "None": return None
            raise NameError(f"Undefined variable: {node.id}")
        raise TypeError(f"Unsupported name context: {type(node.ctx)}")

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        # Block access to private/dangerous attributes
        if node.attr.startswith("_"):
            raise AttributeError(f"Access to private attribute '{node.attr}' is blocked")

        obj = self.visit(node.value)
        try:
            return getattr(obj, node.attr)
        except (AttributeError, TypeError):
             # Try dictionary access as fallback for dot notation
             try:
                 return obj[node.attr]
             except (KeyError, TypeError):
                 raise AttributeError(f"'{type(obj).__name__}' object has no attribute or key '{node.attr}'")

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        obj = self.visit(node.value)
        key = self.visit(node.slice)
        try:
            return obj[key]
        except (KeyError, IndexError, TypeError):
            raise

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type: Type[ast.operator] = type(node.op)
        if op_type in self.ALLOWED_OPERATORS:
            return self.ALLOWED_OPERATORS[op_type](left, right) # type: ignore
        raise TypeError(f"Unsupported operator: {op_type.__name__}")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        operand = self.visit(node.operand)
        op_type: Type[ast.unaryop] = type(node.op)
        if op_type in self.ALLOWED_OPERATORS:
            return self.ALLOWED_OPERATORS[op_type](operand) # type: ignore
        raise TypeError(f"Unsupported unary operator: {op_type.__name__}")

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        values = [self.visit(v) for v in node.values]
        op_type: Type[ast.boolop] = type(node.op)
        if op_type == ast.And:
            res = values[0]
            for v in values[1:]:
                res = res and v
            return res
        if op_type == ast.Or:
            res = values[0]
            for v in values[1:]:
                res = res or v
            return res
        raise TypeError(f"Unsupported boolean operator: {op_type.__name__}")

    def visit_Compare(self, node: ast.Compare) -> Any:
        left = self.visit(node.left)
        for op, right_node in zip(node.ops, node.comparators):
            right = self.visit(right_node)
            op_type: Type[ast.cmpop] = type(op)
            if op_type not in self.ALLOWED_OPERATORS:
                raise TypeError(f"Unsupported comparison operator: {op_type.__name__}")
            if not self.ALLOWED_OPERATORS[op_type](left, right): # type: ignore
                return False
            left = right
        return True

    def visit_List(self, node: ast.List) -> List[Any]:
        return [self.visit(elt) for elt in node.elts]

    def visit_Dict(self, node: ast.Dict) -> Dict[Any, Any]:
        return {self.visit(k): self.visit(v) for k, v in zip(node.keys, node.values) if k is not None}

    def generic_visit(self, node: ast.AST) -> Any:
        raise TypeError(f"Unsupported expression node: {type(node).__name__}")

class Environment:
    """
    Manages global configuration for the template engine.
    """
    def __init__(self, filters: Optional[Dict[str, Callable[[Any], Any]]] = None):
        """
        Initializes the environment.

        Args:
            filters: Custom filters to register.
        """
        self.filters = DEFAULT_FILTERS.copy()
        if filters:
            self.filters.update(filters)

    def from_string(self, source: str) -> "Template":
        """
        Creates a Template object from a source string.

        Args:
            source: The template source code.

        Returns:
            A Template object.
        """
        return Template(source, self)

    def register_filter(self, name: str, func: Callable[[Any], Any]) -> None:
        """Registers a custom filter."""
        self.filters[name] = func

class Template:
    """
    Represents a compiled template that can be rendered with a context.
    """
    def __init__(self, source: str, env: Optional[Environment] = None):
        """
        Initializes the template.

        Args:
            source: The template source code.
            env: The environment to use (optional).
        """
        self.env = env or Environment()
        self.source = source
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        self.ast = parser.parse()

    def render(self, **context: Any) -> str:
        """
        Renders the template with the given context.

        Args:
            **context: Variables to use in the template.

        Returns:
            The rendered template as a string.
        """
        return self._render_node(self.ast, context)

    def _render_node(self, node: Node, context: Dict[str, Any]) -> str:
        """Internal method to recursively render AST nodes."""
        if isinstance(node, RootNode):
            return "".join(self._render_node(child, context) for child in node.children)

        elif isinstance(node, TextNode):
            return node.value

        elif isinstance(node, ExpressionNode):
            result = self._evaluate_expression(node.expression, context, node)
            return escape_html(result)

        elif isinstance(node, IfNode):
            condition_met = self._evaluate_expression(node.condition, context, node)
            if condition_met:
                return "".join(self._render_node(child, context) for child in node.body)
            return ""

        elif isinstance(node, EachNode):
            items = self._evaluate_expression(node.items_expr, context, node)
            if not hasattr(items, "__iter__"):
                return ""

            output = []
            for item in items:
                # Create a new context for the loop
                loop_context = context.copy()
                loop_context[node.item_name] = item
                output.append("".join(self._render_node(child, loop_context) for child in node.body))
            return "".join(output)

        return ""

    def _evaluate_expression(self, expression: str, context: Dict[str, Any], node: Node) -> Any:
        """Evaluates an expression with filters, using a safe evaluator."""
        # Simple parser for expression | filter1 | filter2
        # Need to handle pipes inside strings.
        # This is a bit complex, let's use a simpler approach first:
        # Check if the expression contains pipes.

        # Proper splitting of expr | filters while respecting quotes:
        parts: List[str] = []
        current_part: List[str] = []
        in_quote = None
        for i, char in enumerate(expression):
            if char in ("'", '"'):
                if in_quote == char:
                    in_quote = None
                elif in_quote is None:
                    in_quote = char

            if char == "|" and in_quote is None:
                parts.append("".join(current_part).strip())
                current_part = []
            else:
                current_part.append(char)
        parts.append("".join(current_part).strip())

        expr_core = parts[0]
        filters = parts[1:]

        try:
            # Parse the core expression into an AST
            tree = ast.parse(expr_core, mode="eval")
            evaluator = SafeEvaluator(context)
            value = evaluator.evaluate(tree)

            # Apply filters
            for filter_name in filters:
                if filter_name not in self.env.filters:
                    raise NameError(f"Unknown filter '{filter_name}'")
                value = self.env.filters[filter_name](value)

            return value
        except Exception as e:
            # Wrap the error with line/column info
            raise RuntimeError(f"Error evaluating '{expression}': {str(e)} at line {node.line}, column {node.column}") from e
