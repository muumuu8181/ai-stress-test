import os
import re
import csv
import io
from typing import Any, Dict, List, Optional, Callable, Union, Set
from .lexer import Lexer
from .parser import Parser
from .nodes import Node, RootNode, ExtendsNode, BlockNode, IfNode, ForNode
from .filters import DEFAULT_FILTERS

class Environment:
    """
    Manages the template loading and configuration.

    Attributes:
        loader: A callable that takes a template name and returns its source.
        autoescape: Whether to automatically escape HTML characters in variables.
        filters: A dictionary of available filters.
        globals: A dictionary of global variables available in all templates.
    """
    def __init__(self, loader: Optional[Callable[[str], Optional[str]]] = None, autoescape: bool = True):
        """Initializes the environment."""
        self.loader = loader
        self.autoescape = autoescape
        self.filters: Dict[str, Callable] = DEFAULT_FILTERS.copy()
        self.globals: Dict[str, Any] = {}

    def get_template(self, name: str) -> 'Template':
        """
        Loads and compiles a template by name.

        Args:
            name: The name of the template.

        Returns:
            A Template object.

        Raises:
            RuntimeError: If no loader is configured.
            FileNotFoundError: If the template is not found.
        """
        if not self.loader:
            raise RuntimeError("No template loader configured")
        source = self.loader(name)
        if source is None:
             raise FileNotFoundError(f"Template '{name}' not found")
        return Template(source, self, name)

    def evaluate_expression(self, expression: str, context: Dict[str, Any], line: int, column: int) -> Any:
        """
        Evaluates an expression within a given context.

        Args:
            expression: The expression string.
            context: Variables available for the expression.
            line: Current line number.
            column: Current column number.

        Returns:
            The result of evaluation.
        """
        expr = expression.strip()
        if "|" in expr:
            parts = self._split_by_unescaped(expr, '|')
            if len(parts) > 1:
                value = self.evaluate_expression(parts[0], context, line, column)
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
        return self._eval_logical(expr, context, line, column)

    def _split_by_unescaped(self, text: str, char: str) -> List[str]:
        """Splits text by char if not inside quotes."""
        parts = []
        current = []
        in_quote = None
        for i, c in enumerate(text):
            if c in ('"', "'") and (i == 0 or text[i-1] != '\\'):
                if in_quote == c:
                    in_quote = None
                elif in_quote is None:
                    in_quote = c

            if c == char and in_quote is None:
                parts.append("".join(current).strip())
                current = []
            else:
                current.append(c)
        parts.append("".join(current).strip())
        return parts

    def _eval_logical(self, expr: str, context: Dict[str, Any], line: int, column: int) -> Any:
        """Evaluates logical and/or/not operators."""
        parts = self._split_by_unescaped_word(expr, 'or')
        if len(parts) > 1:
            for part in parts:
                if self._eval_logical(part, context, line, column):
                    return True
            return False

        parts = self._split_by_unescaped_word(expr, 'and')
        if len(parts) > 1:
            for part in parts:
                if not self._eval_logical(part, context, line, column):
                    return False
            return True

        if expr.startswith("not "):
             return not self._eval_logical(expr[4:].strip(), context, line, column)

        return self._eval_comparison(expr, context, line, column)

    def _split_by_unescaped_word(self, text: str, word: str) -> List[str]:
        """Splits text by word (surrounded by space) if not inside quotes."""
        parts = []
        current = []
        in_quote = None
        word_spaced = f" {word} "

        i = 0
        while i < len(text):
            c = text[i]
            if c in ('"', "'") and (i == 0 or text[i-1] != '\\'):
                if in_quote == c:
                    in_quote = None
                elif in_quote is None:
                    in_quote = c

            if in_quote is None and text.startswith(word_spaced, i):
                parts.append("".join(current).strip())
                current = []
                i += len(word_spaced) - 1 # i will be incremented by 1 later
            else:
                current.append(c)
            i += 1

        parts.append("".join(current).strip())
        return parts

    def _eval_comparison(self, expr: str, context: Dict[str, Any], line: int, column: int) -> Any:
        """Evaluates comparison operators, including chained ones."""
        ops = ["==", "!=", ">=", "<=", ">", "<"]

        # Find all comparison operators not in quotes
        matches = []
        in_quote = None
        for i, c in enumerate(expr):
            if c in ('"', "'") and (i == 0 or expr[i-1] != '\\'):
                if in_quote == c:
                    in_quote = None
                elif in_quote is None:
                    in_quote = c

            if in_quote is None:
                for op in ops:
                    if expr.startswith(op, i):
                        # Ensure it's the full operator
                        if op in (">", "<") and i + 1 < len(expr) and expr[i+1] == "=":
                            continue # Wait for >= or <=
                        matches.append((i, op))
                        break

        if not matches:
            return self._eval_atom(expr, context, line, column)

        # Chained comparisons: a < b < c
        operands = []
        found_ops = []
        last_pos = 0
        for pos, op in matches:
            operands.append(expr[last_pos:pos].strip())
            found_ops.append(op)
            last_pos = pos + len(op)
        operands.append(expr[last_pos:].strip())

        values = [self._eval_atom(op, context, line, column) for op in operands]

        for i in range(len(found_ops)):
            op = found_ops[i]
            v1, v2 = values[i], values[i+1]
            res = False
            if op == "==": res = v1 == v2
            elif op == "!=": res = v1 != v2
            elif op == ">=": res = v1 >= v2
            elif op == "<=": res = v1 <= v2
            elif op == ">": res = v1 > v2
            elif op == "<": res = v1 < v2

            if not res:
                return False
        return True

    def _eval_atom(self, expr: str, context: Dict[str, Any], line: int, column: int) -> Any:
        """Evaluates basic literals and variable lookups."""
        expr = expr.strip()
        if not expr: return None
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        if expr.isdigit():
            return int(expr)
        try:
            return float(expr)
        except ValueError:
            pass
        if expr == "True": return True
        if expr == "False": return False
        if expr == "None": return None
        parts = expr.split(".")
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
             raise NameError(f"Error accessing '{expr}' at line {line}, column {column}: {str(e)}")

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
    """Represents a compiled template ready for rendering."""
    def __init__(self, source: str, environment: Environment, name: Optional[str] = None):
        """
        Initializes the template.

        Args:
            source: The template source string.
            environment: The template environment.
            name: Optional template name.
        """
        self.source = source
        self.environment = environment
        self.name = name
        self.lexer = Lexer(source)
        self.tokens = self.lexer.tokenize()
        self.parser = Parser(self.tokens)
        self.ast = self.parser.parse()

    def render(self, **kwargs: Any) -> str:
        """
        Renders the template with the given context.

        Args:
            **kwargs: Template context variables.

        Returns:
            The rendered template string.
        """
        all_blocks = self._collect_blocks(self.ast)
        visited_templates: Set[str] = set()
        if self.name:
            visited_templates.add(self.name)

        curr = self
        root_template = self
        while True:
            extends_node = curr._find_extends(curr.ast)
            if not extends_node:
                root_template = curr
                break

            parent_name = extends_node.parent_template
            if parent_name in visited_templates:
                raise RuntimeError(f"Cyclic inheritance detected: {parent_name}")
            visited_templates.add(parent_name)

            curr = self.environment.get_template(parent_name)
            parent_blocks = curr._collect_blocks(curr.ast)
            for name, node in parent_blocks.items():
                if name not in all_blocks:
                    all_blocks[name] = node

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
    """
    Creates a file system loader with path traversal protection.

    Args:
        base_path: Base directory for templates.

    Returns:
        A loader callable.
    """
    base_path = os.path.abspath(base_path)
    def loader(name: str) -> Optional[str]:
        target_path = os.path.abspath(os.path.join(base_path, name))
        if not target_path.startswith(base_path):
            raise PermissionError(f"Access denied to template '{name}' (outside of base path)")
        if not os.path.exists(target_path):
            return None
        with open(target_path, "r", encoding="utf-8") as f:
            return f.read()
    return loader
