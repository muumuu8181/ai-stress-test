from typing import List, Any, Optional, Union as TypingUnion

class Node:
    """Base class for all JSONPath AST nodes."""
    pass

class RootNode(Node):
    """Represents the root node '$'."""
    def __repr__(self) -> str:
        return "RootNode()"

class CurrentNode(Node):
    """Represents the current node '@'."""
    def __repr__(self) -> str:
        return "CurrentNode()"

class FieldNode(Node):
    """Represents a field access, e.g., '.store' or '["store"]'."""
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"FieldNode({self.name!r})"

class IndexNode(Node):
    """Represents an array index access, e.g., '[0]' or '[-1]'."""
    def __init__(self, index: int):
        self.index = index

    def __repr__(self) -> str:
        return f"IndexNode({self.index})"

class SliceNode(Node):
    """Represents an array slice, e.g., '[0:5]' or '[:3]'."""
    def __init__(self, start: Optional[int] = None, stop: Optional[int] = None, step: Optional[int] = None):
        self.start = start
        self.stop = stop
        self.step = step

    def __repr__(self) -> str:
        return f"SliceNode(start={self.start}, stop={self.stop}, step={self.step})"

class WildcardNode(Node):
    """Represents a wildcard '*', e.g., '.*' or '[*]'."""
    def __repr__(self) -> str:
        return "WildcardNode()"

class RecursiveDescentNode(Node):
    """Represents recursive descent '..'."""
    def __repr__(self) -> str:
        return "RecursiveDescentNode()"

class UnionNode(Node):
    """Represents a multiple selector, e.g., '["store", "office"]'."""
    def __init__(self, selectors: List[Node]):
        self.selectors = selectors

    def __repr__(self) -> str:
        return f"UnionNode({self.selectors!r})"

class FilterNode(Node):
    """Represents a filter expression, e.g., '[?(@.price < 10)]'."""
    def __init__(self, expression: 'ExpressionNode'):
        self.expression = expression

    def __repr__(self) -> str:
        return f"FilterNode({self.expression!r})"

class ExpressionNode(Node):
    """Base class for expressions used in filters."""
    pass

class BinaryExpressionNode(ExpressionNode):
    """Represents a binary operation in a filter, e.g., '@.price < 10'."""
    def __init__(self, left: Any, operator: str, right: Any):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"BinaryExpressionNode({self.left!r}, {self.operator!r}, {self.right!r})"

class UnaryExpressionNode(ExpressionNode):
    """Represents a unary operation in a filter, e.g., 'not @.price'."""
    def __init__(self, operator: str, operand: Any):
        self.operator = operator
        self.operand = operand

    def __repr__(self) -> str:
        return f"UnaryExpressionNode({self.operator!r}, {self.operand!r})"

class PathExpressionNode(ExpressionNode):
    """Represents a path within an expression, e.g., '@.price'."""
    def __init__(self, nodes: List[Node]):
        self.nodes = nodes

    def __repr__(self) -> str:
        return f"PathExpressionNode({self.nodes!r})"

class LiteralNode(ExpressionNode):
    """Represents a literal value in an expression, e.g., 10 or 'string'."""
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self) -> str:
        return f"LiteralNode({self.value!r})"
