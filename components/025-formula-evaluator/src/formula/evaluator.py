from typing import Any, List, Optional, Union, TYPE_CHECKING
from .parser import ASTNode, NumberNode, StringNode, CellNode, RangeNode, BinaryOpNode, FunctionCallNode
from .functions import FUNCTIONS
from .cell import ERROR_REF, ERROR_VALUE, ERROR_DIV0, ERROR_NAME, ERROR_CIRC, is_error

if TYPE_CHECKING:
    from .sheet import SpreadsheetManager

class Evaluator:
    """
    Evaluator for the parsed formula structure.
    """

    def __init__(self, manager: 'SpreadsheetManager', current_sheet_name: str) -> None:
        """
        Initialize the evaluator.

        Args:
            manager: The SpreadsheetManager instance.
            current_sheet_name: The name of the sheet being evaluated.
        """
        self.manager = manager
        self.current_sheet_name = current_sheet_name

    def evaluate(self, node: ASTNode) -> Any:
        """
        Evaluate an AST node and return its value.

        Args:
            node: The root AST node.

        Returns:
            The result of the evaluation.
        """
        if isinstance(node, NumberNode):
            return node.value

        if isinstance(node, StringNode):
            return node.value

        if isinstance(node, CellNode):
            sheet, addr = self.manager.resolve_reference(self.current_sheet_name, node.address)
            if not sheet:
                return ERROR_REF
            cell = sheet.get_cell(addr)
            return cell.value

        if isinstance(node, RangeNode):
            # Returns a 2D list of values
            return self.manager.get_range(self.current_sheet_name, node.range_ref)

        if isinstance(node, BinaryOpNode):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)

            # Error propagation
            if is_error(left):
                return left
            if is_error(right):
                return right

            try:
                if node.op == "+":
                    return float(left) + float(right)
                if node.op == "-":
                    return float(left) - float(right)
                if node.op == "*":
                    return float(left) * float(right)
                if node.op == "/":
                    if float(right) == 0:
                        return ERROR_DIV0
                    return float(left) / float(right)
            except (ValueError, TypeError):
                return ERROR_VALUE

        if isinstance(node, FunctionCallNode):
            if node.name not in FUNCTIONS:
                return ERROR_NAME

            args = []
            for arg in node.args:
                args.append(self.evaluate(arg))

            try:
                return FUNCTIONS[node.name](args)
            except Exception:
                return ERROR_VALUE

        return None
