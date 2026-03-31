import os
import re
import csv
import io
from typing import Any, Dict, List, Optional, Callable
from .lexer import Lexer
from .parser import Parser
from .nodes import Node, RootNode, ExtendsNode, BlockNode, IfNode, ForNode
from .filters import DEFAULT_FILTERS

class Environment:
    """
    Manages the template loading and configuration.
    """
    def __init__(self, loader: Optional[Callable[[str], Optional[str]]] = None, autoescape: bool = True):
        self.loader = loader
        self.autoescape = autoescape
        self.filters: Dict[str, Callable] = DEFAULT_FILTERS.copy()
        self.globals: Dict[str, Any] = {}

    def get_template(self, name: str) -> 'Template':
        if not self.loader:
            raise RuntimeError("No template loader configured")
        source = self.loader(name)
        if source is None:
             raise FileNotFoundError(f"Template '{name}' not found")
        return Template(source, self, name)

    def evaluate_expression(self, expression: str, context: Dict[str, Any], line: int, column: int) -> Any:
        """Evaluates a simple expression within a given context."""
        # Handle filters
        if "|" in expression:
            parts = [p.strip() for p in re.split(r'\|(?=(?:[^"]*"[^"]*")*[^"]*$)', expression)]
            base_expr = parts[0]
            value = self.evaluate_expression(base_expr, context, line, column)
            for filter_part in parts[1:]:
                if "(" in filter_part and filter_part.endswith(")"):
                    filter_name = filter_part[:filter_part.find("(")].strip()
                    args_str = filter_part[filter_part.find("(")+1:-1]
                    f = io.StringIO(args_str)
                    reader = csv.reader(f, quotechar='"', skipinitialspace=True)
                    try:
                        filter_args = next(reader)
                    except StopIteration:
                        filter_args = []
                else:
                    filter_name = filter_part
                    filter_args = []

                if filter_name not in self.filters:
                    raise NameError(f"Unknown filter '{filter_name}' at line {line}")
                value = self.filters[filter_name](value, *filter_args)
            return value

        # Handle comparisons
        for op in ["==", "!=", ">=", "<=", ">", "<"]:
            if op in expression:
                # We need to ensure we split on the actual operator, not inside strings.
                # Simplified: assuming no strings contain operators.
                parts = expression.split(op, 1)
                if len(parts) == 2:
                    left_val = self.evaluate_expression(parts[0].strip(), context, line, column)
                    right_val = self.evaluate_expression(parts[1].strip(), context, line, column)
                    if op == "==": return left_val == right_val
                    if op == "!=": return left_val != right_val
                    if op == ">=": return left_val >= right_val
                    if op == "<=": return left_val <= right_val
                    if op == ">": return left_val > right_val
                    if op == "<": return left_val < right_val

        # Handle literals
        if expression.startswith(('"', "'")) and expression.endswith(('"', "'")):
            return expression[1:-1]
        if expression.isdigit():
            return int(expression)
        if expression == "True": return True
        if expression == "False": return False
        if expression == "None": return None

        # Handle variable access
        parts = expression.split(".")
        try:
            if parts[0] in context:
                val = context[parts[0]]
            elif parts[0] in self.globals:
                val = self.globals[parts[0]]
            else:
                raise NameError(f"Undefined variable '{parts[0]}' at line {line}, column {column}")

            for part in parts[1:]:
                if isinstance(val, dict):
                    if part in val:
                        val = val[part]
                    else:
                        raise NameError(f"Undefined attribute '{part}' in dict at line {line}, column {column}")
                else:
                    if hasattr(val, part):
                        val = getattr(val, part)
                    else:
                        raise NameError(f"Undefined attribute '{part}' in '{type(val).__name__}' at line {line}, column {column}")
            return val
        except NameError:
            raise
        except Exception as e:
             raise NameError(f"Error accessing '{expression}' at line {line}, column {column}: {str(e)}")

class RenderWrapper:
    """A wrapper for Environment during rendering to keep blocks thread-safe."""
    def __init__(self, env: Environment, blocks: Dict[str, BlockNode]):
        self.env = env
        self.blocks = blocks
        self.autoescape = env.autoescape
    def evaluate_expression(self, *args, **kwargs):
        return self.env.evaluate_expression(*args, **kwargs)
    def get_template(self, *args, **kwargs):
        return self.env.get_template(*args, **kwargs)

class Template:
    """Represents a compiled template."""
    def __init__(self, source: str, environment: Environment, name: Optional[str] = None):
        self.source = source
        self.environment = environment
        self.name = name
        self.lexer = Lexer(source)
        self.tokens = self.lexer.tokenize()
        self.parser = Parser(self.tokens)
        self.ast = self.parser.parse()

    def render(self, **kwargs: Any) -> str:
        """Renders the template with the given context."""
        # Multi-level inheritance support:
        # Start with blocks in THIS template.
        # If we extend, the CHILD template's blocks should override PARENT's.
        # This means we should start with the LEAF template,
        # collect all its blocks, then walk up the inheritance chain,
        # only adding blocks that haven't been seen yet.

        leaf_template = self
        all_blocks = self._collect_blocks(self.ast)

        # Traverse up to find the root template
        curr = self
        while True:
            extends_node = curr._find_extends(curr.ast)
            if not extends_node:
                root_template = curr
                break
            curr = self.environment.get_template(extends_node.parent_template)
            # Add blocks from parents IF they are not already in all_blocks
            parent_blocks = curr._collect_blocks(curr.ast)
            for name, node in parent_blocks.items():
                if name not in all_blocks:
                    all_blocks[name] = node

        # Now render starting from root_template, using all_blocks
        wrapper = RenderWrapper(self.environment, all_blocks)
        return root_template.ast.render(kwargs, wrapper)

    def _find_extends(self, node: RootNode) -> Optional[ExtendsNode]:
        """Finds the first ExtendsNode in the AST."""
        for child in node.children:
            if isinstance(child, ExtendsNode):
                return child
        return None

    def _collect_blocks(self, node: RootNode) -> Dict[str, BlockNode]:
        """Collects all BlockNodes in the AST."""
        blocks: Dict[str, BlockNode] = {}
        def _walk(n: Node) -> None:
            if isinstance(n, RootNode):
                for c in n.children: _walk(c)
            elif isinstance(n, BlockNode):
                blocks[n.name] = n
                for c in n.body_nodes: _walk(c)
            elif isinstance(n, IfNode):
                for c in n.then_nodes: _walk(c)
                for _, body in n.elif_nodes:
                    for c in body: _walk(c)
                for c in n.else_nodes: _walk(c)
            elif isinstance(n, ForNode):
                for c in n.body_nodes: _walk(c)
        _walk(node)
        return blocks

def FileSystemLoader(base_path: str) -> Callable[[str], Optional[str]]:
    """Creates a simple file system loader."""
    def loader(name: str) -> Optional[str]:
        path = os.path.join(base_path, name)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return loader
