import os
import re
import csv
import io
from typing import Any, Dict, List, Optional, Callable, Union
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
        """Evaluates an expression within a given context."""
        expr = expression.strip()
        if "|" in expr:
            parts = [p.strip() for p in re.split(r'\|(?=(?:[^\"\']*\"[^\"\']*\")*[^\"\']*$)', expr)]
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

    def _eval_logical(self, expr: str, context: Dict[str, Any], line: int, column: int) -> Any:
        # Handle 'or'
        pattern_or = r'\sor\s(?=(?:[^\"\']*\"[^\"\']*\")*[^\"\']*$)'
        parts = [p.strip() for p in re.split(pattern_or, expr)]
        if len(parts) > 1:
            for part in parts:
                if self._eval_logical(part, context, line, column):
                    return True
            return False

        # Handle 'and'
        pattern_and = r'\sand\s(?=(?:[^\"\']*\"[^\"\']*\")*[^\"\']*$)'
        parts = [p.strip() for p in re.split(pattern_and, expr)]
        if len(parts) > 1:
            for part in parts:
                if not self._eval_logical(part, context, line, column):
                    return False
            return True

        # Handle 'not'
        if expr.startswith("not "):
             return not self._eval_logical(expr[4:].strip(), context, line, column)

        # Handle comparisons
        for op in ["==", "!=", ">=", "<=", ">", "<"]:
            op_escaped = re.escape(op)
            # Use negative lookbehind/lookahead to avoid matching substring of other ops
            # and a lookahead to ensure we are not inside quotes.
            # However, the quote lookahead `(?=(?:[^\"\']*\"[^\"\']*\")*[^\"\']*$)`
            # only works if there are NO escaped quotes.
            # Given standard library only and simple requirements, this is usually acceptable.
            pattern = rf"(?<![=<>!]){op_escaped}(?![=<>!])"

            # Find all potential matches
            matches = list(re.finditer(pattern, expr))
            for m in reversed(matches):
                # Check if this match is outside quotes
                start = m.start()
                if (expr[:start].count('"') % 2 == 0) and (expr[:start].count("'") % 2 == 0):
                    left_expr = expr[:m.start()].strip()
                    right_expr = expr[m.end():].strip()
                    left_val = self._eval_logical(left_expr, context, line, column)
                    right_val = self._eval_logical(right_expr, context, line, column)
                    if op == "==": return left_val == right_val
                    if op == "!=": return left_val != right_val
                    if op == ">=": return left_val >= right_val
                    if op == "<=": return left_val <= right_val
                    if op == ">": return left_val > right_val
                    if op == "<": return left_val < right_val
                    break

        return self._eval_atom(expr, context, line, column)

    def _eval_atom(self, expr: str, context: Dict[str, Any], line: int, column: int) -> Any:
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
    def __init__(self, env: Environment, blocks: Dict[str, BlockNode]):
        self.env = env
        self.blocks = blocks
        self.autoescape = env.autoescape
    def evaluate_expression(self, *args, **kwargs):
        return self.env.evaluate_expression(*args, **kwargs)
    def get_template(self, *args, **kwargs):
        return self.env.get_template(*args, **kwargs)

class Template:
    def __init__(self, source: str, environment: Environment, name: Optional[str] = None):
        self.source = source
        self.environment = environment
        self.name = name
        self.lexer = Lexer(source)
        self.tokens = self.lexer.tokenize()
        self.parser = Parser(self.tokens)
        self.ast = self.parser.parse()

    def render(self, **kwargs: Any) -> str:
        all_blocks = self._collect_blocks(self.ast)
        curr = self
        while True:
            extends_node = curr._find_extends(curr.ast)
            if not extends_node:
                root_template = curr
                break
            curr = self.environment.get_template(extends_node.parent_template)
            parent_blocks = curr._collect_blocks(curr.ast)
            for name, node in parent_blocks.items():
                if name not in all_blocks:
                    all_blocks[name] = node
        wrapper = RenderWrapper(self.environment, all_blocks)
        return root_template.ast.render(kwargs, wrapper)

    def _find_extends(self, node: RootNode) -> Optional[ExtendsNode]:
        for child in node.children:
            if isinstance(child, ExtendsNode):
                return child
        return None

    def _collect_blocks(self, node: RootNode) -> Dict[str, BlockNode]:
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
    def loader(name: str) -> Optional[str]:
        path = os.path.join(base_path, name)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return loader
