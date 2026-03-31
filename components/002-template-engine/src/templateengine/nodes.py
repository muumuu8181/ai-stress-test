from abc import ABC, abstractmethod
from typing import List, Any, Dict, Optional

class Node(ABC):
    @abstractmethod
    def render(self, context: Dict[str, Any], environment: Any) -> str:
        pass

class RootNode(Node):
    def __init__(self, children: List[Node]):
        self.children = children

    def render(self, context: Dict[str, Any], environment: Any) -> str:
        return "".join(child.render(context, environment) for child in self.children)

class TextNode(Node):
    def __init__(self, text: str):
        self.text = text

    def render(self, context: Dict[str, Any], environment: Any) -> str:
        return self.text

class VariableNode(Node):
    def __init__(self, expression: str, line: int, column: int):
        self.expression = expression.strip()
        self.line = line
        self.column = column

    def render(self, context: Dict[str, Any], environment: Any) -> str:
        try:
            value = environment.evaluate_expression(self.expression, context, self.line, self.column)
            if hasattr(value, "__html__"):
                return str(value.__html__())
            if environment.autoescape:
                from html import escape
                return escape(str(value))
            return str(value)
        except Exception as e:
            if not hasattr(e, 'line'):
                e.line = self.line
                e.column = self.column
            raise e

class IfNode(Node):
    def __init__(self, condition: str, then_nodes: List[Node], elif_nodes: List[tuple], else_nodes: List[Node], line: int, column: int):
        self.condition = condition.strip()
        self.then_nodes = then_nodes
        self.elif_nodes = elif_nodes # List of (condition, nodes)
        self.else_nodes = else_nodes
        self.line = line
        self.column = column

    def render(self, context: Dict[str, Any], environment: Any) -> str:
        if environment.evaluate_expression(self.condition, context, self.line, self.column):
            return "".join(node.render(context, environment) for node in self.then_nodes)

        for condition, nodes in self.elif_nodes:
            if environment.evaluate_expression(condition.strip(), context, self.line, self.column):
                return "".join(node.render(context, environment) for node in nodes)

        if self.else_nodes:
            return "".join(node.render(context, environment) for node in self.else_nodes)

        return ""

class ForNode(Node):
    def __init__(self, item_name: str, collection_expr: str, body_nodes: List[Node], line: int, column: int):
        self.item_name = item_name.strip()
        self.collection_expr = collection_expr.strip()
        self.body_nodes = body_nodes
        self.line = line
        self.column = column

    def render(self, context: Dict[str, Any], environment: Any) -> str:
        collection = environment.evaluate_expression(self.collection_expr, context, self.line, self.column)
        result = []
        for item in collection:
            new_context = context.copy()
            new_context[self.item_name] = item
            for node in self.body_nodes:
                result.append(node.render(new_context, environment))
        return "".join(result)

class ExtendsNode(Node):
    def __init__(self, parent_template: str, line: int, column: int):
        self.parent_template = parent_template.strip().strip('"').strip("'")
        self.line = line
        self.column = column

    def render(self, context: Dict[str, Any], environment: Any) -> str:
        return ""

class BlockNode(Node):
    def __init__(self, name: str, body_nodes: List[Node], line: int, column: int):
        self.name = name.strip()
        self.body_nodes = body_nodes
        self.line = line
        self.column = column

    def render(self, context: Dict[str, Any], environment: Any) -> str:
        # Check if this block is overridden in the current render context
        if hasattr(environment, 'blocks') and self.name in environment.blocks:
            block_to_render = environment.blocks[self.name]
            if block_to_render is self:
                # Original content
                return "".join(node.render(context, environment) for node in self.body_nodes)
            else:
                return block_to_render.render(context, environment)
        return "".join(node.render(context, environment) for node in self.body_nodes)
