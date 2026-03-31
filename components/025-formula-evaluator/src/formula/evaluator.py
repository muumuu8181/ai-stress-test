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
            # Range evaluation returns 2D list for all range types
            sheet, rest = self.manager.resolve_reference(self.current_sheet_name, node.range_ref)
            if not sheet or ':' not in rest:
                return ERROR_REF

            start_ref, end_ref = rest.split(':')
            try:
                s_row, s_col = sheet.parse_address(start_ref)
                e_row, e_col = sheet.parse_address(end_ref)

                # Handling of column-wide ranges
                if s_row is None and e_row is None:
                    # e.g. A:B. We need to collect all rows for these columns.
                    # As a spreadsheet, we'll collect up to the last non-empty row.
                    max_row = 0
                    for cell_addr in sheet.cells:
                        r, c = sheet.parse_address(cell_addr)
                        if r is not None:
                            max_row = max(max_row, r)

                    rows = []
                    for r in range(max_row + 1):
                        row = []
                        for c in range(min(s_col, e_col), max(s_col, e_col) + 1):
                            addr = sheet.to_address(r, c)
                            row.append(sheet.get_cell(addr).value)
                        rows.append(row)
                    return rows

                if s_row is not None and e_row is not None:
                    rows = []
                    for r in range(min(s_row, e_row), max(s_row, e_row) + 1):
                        row = []
                        for c in range(min(s_col, e_col), max(s_col, e_col) + 1):
                            addr = sheet.to_address(r, c)
                            row.append(sheet.get_cell(addr).value)
                        rows.append(row)
                    return rows

                return ERROR_REF
            except ValueError:
                return ERROR_REF

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
