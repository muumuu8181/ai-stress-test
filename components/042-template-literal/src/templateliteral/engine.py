import re
from typing import Any, Dict, List, Optional, Callable
from .lexer import Lexer
from .parser import Parser, TemplateSyntaxError
from .nodes import Node, RootNode, TextNode, ExpressionNode, IfNode, EachNode
from .filters import DEFAULT_FILTERS, escape_html, SafeString

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
        """Evaluates an expression with filters, supporting dot notation for attributes and keys."""
        parts = [p.strip() for p in expression.split("|")]
        expr_core = parts[0]
        filters = parts[1:]

        try:
            # Simple attribute/key resolver for dot notation
            def resolve_dotted_path(path: str, ctx: Dict[str, Any]) -> Any:
                bits = path.split(".")
                val = ctx.get(bits[0])
                if val is None and bits[0] not in ctx:
                     # Check if it's a literal or other expression
                     return eval(path, {"__builtins__": {}}, ctx)

                for bit in bits[1:]:
                    try:
                        # Try attribute access first
                        val = getattr(val, bit)
                    except (AttributeError, TypeError):
                        try:
                            # Then try dictionary key access
                            val = val[bit]
                        except (KeyError, TypeError):
                            raise NameError(f"Could not resolve '{bit}' in '{path}'")
                return val

            # Check if it's a simple name or dotted path, otherwise use eval
            if re.match(r"^[a-zA-Z_][a-zA-Z0-9_.]*$", expr_core):
                value = resolve_dotted_path(expr_core, context)
            else:
                value = eval(expr_core, {"__builtins__": {}}, context)

            # Apply filters
            for filter_name in filters:
                if filter_name not in self.env.filters:
                    raise NameError(f"Unknown filter '{filter_name}'")
                value = self.env.filters[filter_name](value)

            return value
        except Exception as e:
            # Wrap the error with line/column info
            raise RuntimeError(f"Error evaluating '{expression}': {str(e)} at line {node.line}, column {node.column}") from e
