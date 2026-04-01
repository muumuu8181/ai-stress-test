from typing import List, Any, Optional

class Node:
    """Base class for all AST nodes."""
    def __init__(self, line: int, column: int):
        self.line = line
        self.column = column

    def render(self, context: dict) -> str:
        """Renders the node to a string."""
        raise NotImplementedError("Subclasses must implement render()")

class RootNode(Node):
    """Root node containing a list of child nodes."""
    def __init__(self, children: List[Node]):
        super().__init__(1, 1)
        self.children = children

    def render(self, context: dict) -> str:
        return "".join(node.render(context) for node in self.children)

class TextNode(Node):
    """Represents literal text."""
    def __init__(self, value: str, line: int, column: int):
        super().__init__(line, column)
        self.value = value

    def render(self, context: dict) -> str:
        return self.value

class ExpressionNode(Node):
    """Represents an expression for evaluation, e.g., ${variable}."""
    def __init__(self, expression: str, line: int, column: int):
        super().__init__(line, column)
        self.expression = expression

    def render(self, context: dict) -> str:
        # The engine will handle expression evaluation and filters
        # This node just holds the expression string
        return f"${{{self.expression}}}"

class IfNode(Node):
    """Represents a conditional block: {?condition}...{/?}."""
    def __init__(self, condition: str, body: List[Node], line: int, column: int):
        super().__init__(line, column)
        self.condition = condition
        self.body = body

    def render(self, context: dict) -> str:
        # Evaluation is handled by the engine
        return "".join(node.render(context) for node in self.body)

class EachNode(Node):
    """Represents a loop block: {@each items as item}...{/each}."""
    def __init__(self, items_expr: str, item_name: str, body: List[Node], line: int, column: int):
        super().__init__(line, column)
        self.items_expr = items_expr
        self.item_name = item_name
        self.body = body

    def render(self, context: dict) -> str:
        # Loop logic is handled by the engine
        return "".join(node.render(context) for node in self.body)
