from typing import List, Any, Dict, Union as TypingUnion, Optional
from .nodes import (
    Node, RootNode, CurrentNode, FieldNode, IndexNode, SliceNode,
    WildcardNode, RecursiveDescentNode, UnionNode, FilterNode,
    ExpressionNode, BinaryExpressionNode, UnaryExpressionNode,
    PathExpressionNode, LiteralNode
)

class Match:
    """Represents a matched value and its location (for update/delete)."""
    def __init__(self, value: Any, parent: Any = None, key: Any = None):
        self.value = value
        self.parent = parent
        self.key = key

    def __repr__(self) -> str:
        return f"Match(value={self.value!r})"

class Evaluator:
    """Evaluates a JSONPath AST against a JSON-like object."""

    def __init__(self, data: Any):
        self.root_data = data

    def evaluate(self, nodes: List[Node]) -> List[Match]:
        matches = [Match(self.root_data)]
        for node in nodes:
            next_matches = []
            for match in matches:
                next_matches.extend(self._evaluate_node(node, match))
            matches = next_matches
        return matches

    def _evaluate_node(self, node: Node, match: Match) -> List[Match]:
        data = match.value
        if isinstance(node, RootNode):
            return [Match(self.root_data)]
        elif isinstance(node, CurrentNode):
            return [match]
        elif isinstance(node, PathExpressionNode):
             # Handle nested paths
             evaluator = Evaluator(self.root_data)
             current_matches = [match]
             for sub_node in node.nodes:
                 if isinstance(sub_node, (RootNode, CurrentNode)):
                     continue
                 next_matches = []
                 for m in current_matches:
                     next_matches.extend(self._evaluate_node(sub_node, m))
                 current_matches = next_matches
             return current_matches
        elif isinstance(node, FieldNode):
            if isinstance(data, dict) and node.name in data:
                return [Match(data[node.name], data, node.name)]
            elif node.name == 'length': # Script support: @.length
                if isinstance(data, (list, dict, str)):
                    return [Match(len(data), data, 'length')]
            return []
        elif isinstance(node, IndexNode):
            if isinstance(data, list):
                idx = node.index
                if idx < 0:
                    idx = len(data) + idx
                if 0 <= idx < len(data):
                    return [Match(data[idx], data, idx)]
            return []
        elif isinstance(node, SliceNode):
            if isinstance(data, list):
                res = []
                start = node.start if node.start is not None else 0
                stop = node.stop if node.stop is not None else len(data)
                step = node.step if node.step is not None else 1

                # We need to return matches for each element to support update/delete
                # Standard slice data[start:stop:step] returns a new list
                indices = range(len(data))[start:stop:step]
                for i in indices:
                    res.append(Match(data[i], data, i))
                return res
            return []
        elif isinstance(node, WildcardNode):
            if isinstance(data, dict):
                return [Match(v, data, k) for k, v in data.items()]
            elif isinstance(data, list):
                return [Match(v, data, i) for i, v in enumerate(data)]
            return []
        elif isinstance(node, RecursiveDescentNode):
            return self._recursive_descent(data)
        elif isinstance(node, UnionNode):
            res = []
            for selector in node.selectors:
                res.extend(self._evaluate_node(selector, match))
            return res
        elif isinstance(node, FilterNode):
            if isinstance(data, list):
                res = []
                # If we have a list, we might be filtering the list elements,
                # OR we might be filtering the list itself (e.g. $[?(@.length > 5)]).
                # JSONPath standard for $[?(@.length > 5)] where $ is a list:
                # Usually it filters the elements. But if the expression refers to @.length
                # and @ is the list, it should match the list itself.

                # Check if it matches the list itself first
                if self._evaluate_expression(node.expression, data):
                    # If it matches as a whole, it's ambiguous in some specs,
                    # but usually $[?()] on a list filters elements.
                    pass

                for i, item in enumerate(data):
                    if self._evaluate_expression(node.expression, item):
                        res.append(Match(item, data, i))

                if not res:
                     # Try evaluating against the list itself if no elements matched
                     if self._evaluate_expression(node.expression, data):
                         return [match]
                return res
            else:
                 # Evaluate against the data itself
                 if self._evaluate_expression(node.expression, data):
                     return [match]
            return []
        return []

    def _recursive_descent(self, data: Any) -> List[Match]:
        res = [Match(data)]
        if isinstance(data, dict):
            for k, v in data.items():
                res.extend(self._recursive_descent(v))
        elif isinstance(data, list):
            for item in data:
                res.extend(self._recursive_descent(item))
        return res

    def _evaluate_expression(self, expr: ExpressionNode, current_item: Any) -> Any:
        if isinstance(expr, LiteralNode):
            return expr.value
        elif isinstance(expr, PathExpressionNode):
            # Evaluate path starting from current_item or root
            evaluator = Evaluator(self.root_data)
            # Temporarily set current item for '@'
            matches = [Match(current_item)]

            # Special case for @.length
            if len(expr.nodes) == 2 and isinstance(expr.nodes[0], CurrentNode) and isinstance(expr.nodes[1], FieldNode) and expr.nodes[1].name == 'length':
                if isinstance(current_item, (list, dict, str)):
                    return len(current_item)

            # Optimization: if it's just @, return current_item
            if len(expr.nodes) == 1 and isinstance(expr.nodes[0], CurrentNode):
                return current_item

            for node in expr.nodes:
                if isinstance(node, RootNode):
                    matches = [Match(self.root_data)]
                    continue
                if isinstance(node, CurrentNode):
                    continue

                next_matches = []
                for m in matches:
                    next_matches.extend(self._evaluate_node(node, m))
                matches = next_matches

            if not matches:
                # Still check if it was .length
                if len(expr.nodes) > 1:
                    last_node = expr.nodes[-1]
                    if isinstance(last_node, FieldNode) and last_node.name == 'length':
                         # If we have no matches but we are looking for length,
                         # it might be that the path before .length matched nothing,
                         # OR it matched something but _evaluate_node for FieldNode('length') returned nothing because it's not in the dict.
                         pass

                return None
            if len(matches) == 1:
                return matches[0].value
            return [m.value for m in matches]

        elif isinstance(expr, BinaryExpressionNode):
            left = self._evaluate_expression(expr.left, current_item)
            right = self._evaluate_expression(expr.right, current_item)

            op = expr.operator
            if op == '==': return left == right
            if op == '!=': return left != right
            if op == '<':
                try: return left < right
                except TypeError: return False
            if op == '<=':
                try: return left <= right
                except TypeError: return False
            if op == '>':
                try: return left > right
                except TypeError: return False
            if op == '>=':
                try: return left >= right
                except TypeError: return False
            if op == '&&': return left and right
            if op == '||': return left or right

        elif isinstance(expr, UnaryExpressionNode):
            operand = self._evaluate_expression(expr.operand, current_item)
            if expr.operator == '!':
                return not operand

        return False

    def update(self, nodes: List[Node], value: Any) -> Any:
        matches = self.evaluate(nodes)
        for match in matches:
            if match.parent is not None:
                match.parent[match.key] = value
            else:
                # Root update?
                if isinstance(value, (dict, list)):
                    self.root_data = value
        return self.root_data

    def delete(self, nodes: List[Node]) -> Any:
        matches = self.evaluate(nodes)
        # Sort matches to delete from list in reverse order to keep indices valid
        # This is tricky for nested paths.
        # A simpler way is to collect matches, and if they have parents, remove them.

        # Group by parent to handle list index shifts
        from collections import defaultdict
        parents = defaultdict(list)
        for m in matches:
            if m.parent is not None:
                parents[id(m.parent)].append(m)

        for parent_id, ms in parents.items():
            parent = ms[0].parent
            if isinstance(parent, list):
                # Sort indices in descending order
                indices = sorted([m.key for m in ms], reverse=True)
                for idx in indices:
                    if idx < len(parent):
                        del parent[idx]
            elif isinstance(parent, dict):
                for m in ms:
                    if m.key in parent:
                        del parent[m.key]
        return self.root_data
