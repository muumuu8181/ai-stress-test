import re
from typing import Dict, List, Optional, Tuple, Set, Union
from .cell import Cell, ERROR_CIRC, ERROR_REF, is_error
from .lexer import Lexer
from .parser import Parser, CellNode, RangeNode, BinaryOpNode, FunctionCallNode
from .evaluator import Evaluator

class Sheet:
    """
    Manages a single spreadsheet with cells.
    """

    def __init__(self, name: str, manager: 'SpreadsheetManager') -> None:
        """
        Initialize a sheet with its name.

        Args:
            name: The name of the sheet.
            manager: The SpreadsheetManager instance.
        """
        self.name: str = name
        self.manager = manager
        self.cells: Dict[str, Cell] = {}
        # dependents[cell_addr] = set of cells (as 'Sheet!A1') that depend on cell_addr
        self.dependents: Dict[str, Set[str]] = {}

    def get_cell(self, address: str) -> Cell:
        """
        Get or create a cell at the specified address.

        Args:
            address: The cell address (e.g., 'A1').

        Returns:
            The cell object.
        """
        address = address.upper()
        if address not in self.cells:
            self.cells[address] = Cell(address)
        return self.cells[address]

    def set_cell_value(self, address: str, value: str) -> None:
        """
        Update the value of a cell and trigger recalculation.

        Args:
            address: The cell address.
            value: The raw string value.
        """
        address = address.upper()
        cell = self.get_cell(address)

        # Clear old dependencies
        for dep in list(cell.dependencies):
            sheet, addr = self.manager._resolve_full_reference(self.name, dep)
            if sheet and addr in sheet.dependents:
                sheet.dependents[addr].discard(f"{self.name}!{address}")

        cell.set_value(value)

        # Parse formula to find new dependencies
        if cell.formula:
            try:
                # If formula is just empty or whitespace, it's invalid
                if not cell.formula.strip():
                    raise ValueError("Empty formula")

                lexer = Lexer(cell.formula)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()

                new_deps = self._find_dependencies(ast)
                expanded_deps = set()
                for dep in new_deps:
                    sheet_name, rest = self.manager._split_ref(dep)
                    target_sheet = self.manager.get_sheet(sheet_name or self.name)
                    if target_sheet:
                        if ':' in rest:
                            # Expand range to individual cells
                            cells = self.manager.get_range(sheet_name or self.name, rest)
                            for c in cells:
                                expanded_deps.add(f"{target_sheet.name}!{c.address}")
                        else:
                            expanded_deps.add(f"{target_sheet.name}!{rest}")

                cell.dependencies = expanded_deps

                for dep in expanded_deps:
                    s_name, s_addr = self.manager._split_ref(dep)
                    sheet = self.manager.get_sheet(s_name)
                    if sheet:
                        if s_addr not in sheet.dependents:
                            sheet.dependents[s_addr] = set()
                        sheet.dependents[s_addr].add(f"{self.name}!{address}")
            except Exception:
                # We will set the cell value to #ERROR! in recalculate
                pass

        self.manager.recalculate(f"{self.name}!{address}")

    def _find_dependencies(self, node) -> Set[str]:
        deps = set()
        if isinstance(node, CellNode):
            deps.add(node.address)
        elif isinstance(node, RangeNode):
            deps.add(node.range_ref)
        elif isinstance(node, BinaryOpNode):
            deps.update(self._find_dependencies(node.left))
            deps.update(self._find_dependencies(node.right))
        elif isinstance(node, FunctionCallNode):
            for arg in node.args:
                deps.update(self._find_dependencies(arg))
        return deps

    @staticmethod
    def parse_address(address: str) -> Tuple[Optional[int], int]:
        """
        Parse A1 address into (row, col).
        For column references like 'A', row will be None.
        """
        address = address.upper()
        if '!' in address:
            address = address.split('!')[-1]

        match = re.match(r"^([A-Z]+)([0-9]+)$", address)
        if match:
            col_str, row_str = match.groups()
            col = 0
            for i, char in enumerate(reversed(col_str)):
                col += (ord(char) - ord('A') + 1) * (26 ** i)
            return int(row_str) - 1, col - 1

        match = re.match(r"^([A-Z]+)$", address)
        if match:
            col_str = match.group(1)
            col = 0
            for i, char in enumerate(reversed(col_str)):
                col += (ord(char) - ord('A') + 1) * (26 ** i)
            return None, col - 1

        raise ValueError(f"Invalid address: {address}")

    @staticmethod
    def to_address(row: int, col: int) -> str:
        col_str = ""
        temp_col = col + 1
        while temp_col > 0:
            temp_col, remainder = divmod(temp_col - 1, 26)
            col_str = chr(ord('A') + remainder) + col_str
        return f"{col_str}{row + 1}"


class SpreadsheetManager:
    """
    Manages multiple sheets and provides workbook-level operations.
    """

    def __init__(self) -> None:
        self.sheets: Dict[str, Sheet] = {"Sheet1": Sheet("Sheet1", self)}

    def get_sheet(self, name: str) -> Optional[Sheet]:
        if name.startswith("'") and name.endswith("'"):
            name = name[1:-1]
        return self.sheets.get(name)

    def add_sheet(self, name: str) -> Sheet:
        if name not in self.sheets:
            self.sheets[name] = Sheet(name, self)
        return self.sheets[name]

    def _split_ref(self, ref: str) -> Tuple[Optional[str], str]:
        if '!' in ref:
            if ref.startswith("'"):
                end_quote = ref.find("'", 1)
                if end_quote != -1 and len(ref) > end_quote + 1 and ref[end_quote + 1] == '!':
                    sheet_name = ref[1:end_quote]
                    address = ref[end_quote+2:]
                    return sheet_name, address.upper()

            parts = ref.split('!', 1)
            return parts[0], parts[1].upper()
        return None, ref.upper()

    def resolve_reference(self, current_sheet_name: str, ref: str) -> Tuple[Optional[Sheet], str]:
        sheet_name, address = self._split_ref(ref)
        target_sheet_name = sheet_name if sheet_name else current_sheet_name
        sheet = self.get_sheet(target_sheet_name)
        return sheet, address

    def _resolve_full_reference(self, current_sheet_name: str, full_ref: str) -> Tuple[Optional[Sheet], str]:
        sheet_name, address = self._split_ref(full_ref)
        target_sheet_name = sheet_name if sheet_name else current_sheet_name
        return self.get_sheet(target_sheet_name), address

    def get_range(self, current_sheet_name: str, range_ref: str) -> List[Cell]:
        sheet, rest = self.resolve_reference(current_sheet_name, range_ref)
        if not sheet: return []

        if ':' not in rest:
            try:
                return [sheet.get_cell(rest)]
            except ValueError:
                return []

        start_ref, end_ref = rest.split(':')
        try:
            s_row, s_col = sheet.parse_address(start_ref)
            e_row, e_col = sheet.parse_address(end_ref)

            if s_row is None and e_row is None:
                max_row = 0
                for cell_addr in sheet.cells:
                    r, c = sheet.parse_address(cell_addr)
                    if r is not None:
                        max_row = max(max_row, r)

                cells = []
                for c in range(min(s_col, e_col), max(s_col, e_col) + 1):
                    for r in range(max_row + 1):
                        addr = sheet.to_address(r, c)
                        cells.append(sheet.get_cell(addr))
                return cells

            if s_row is not None and e_row is not None:
                cells = []
                for r in range(min(s_row, e_row), max(s_row, e_row) + 1):
                    for c in range(min(s_col, e_col), max(s_col, e_col) + 1):
                        addr = sheet.to_address(r, c)
                        cells.append(sheet.get_cell(addr))
                return cells
        except ValueError:
            return []
        return []

    def recalculate(self, start_node: str) -> None:
        """
        Recalculate cells affected by the change.
        """
        try:
            visited_for_cycle = set()
            stack = set()
            self._check_cycles(start_node, visited_for_cycle, stack)
        except ValueError:
            sheet_name, addr = self._split_ref(start_node)
            sheet = self.get_sheet(sheet_name)
            if sheet:
                sheet.get_cell(addr).value = ERROR_CIRC
            all_reachable = self._get_all_reachable(start_node)
            for node in all_reachable:
                s_name, s_addr = self._split_ref(node)
                s = self.get_sheet(s_name)
                if s: s.get_cell(s_addr).value = ERROR_CIRC
            return

        all_reachable = self._get_all_reachable(start_node)
        order = self._topological_sort(all_reachable)

        for node in order:
            sheet_name, addr = self._split_ref(node)
            sheet = self.get_sheet(sheet_name)
            if not sheet: continue
            cell = sheet.get_cell(addr)
            if cell.formula:
                evaluator = Evaluator(self, sheet_name)
                try:
                    # If formula is only "=" or has no tokens
                    if not cell.formula.strip():
                         raise ValueError("Empty formula")
                    lexer = Lexer(cell.formula)
                    tokens = lexer.tokenize()
                    parser = Parser(tokens)
                    cell.value = evaluator.evaluate(parser.parse())
                except Exception:
                    cell.value = "#ERROR!"

    def _check_cycles(self, node: str, visited: Set[str], stack: Set[str]):
        visited.add(node)
        stack.add(node)

        sheet_name, addr = self._split_ref(node)
        sheet = self.get_sheet(sheet_name)
        if sheet and addr in sheet.dependents:
            for dep in sheet.dependents[addr]:
                if dep in stack:
                    raise ValueError("Circular reference")
                if dep not in visited:
                    self._check_cycles(dep, visited, stack)
        stack.remove(node)

    def _get_all_reachable(self, start_node: str) -> Set[str]:
        visited = set()
        to_visit = [start_node]
        while to_visit:
            curr = to_visit.pop()
            if curr not in visited:
                visited.add(curr)
                sheet_name, addr = self._split_ref(curr)
                sheet = self.get_sheet(sheet_name)
                if sheet and addr in sheet.dependents:
                    for dep in sheet.dependents[addr]:
                        to_visit.append(dep)
        return visited

    def _topological_sort(self, nodes: Set[str]) -> List[str]:
        result = []
        visited = set()

        def visit(node):
            if node not in visited:
                visited.add(node)
                sheet_name, addr = self._split_ref(node)
                sheet = self.get_sheet(sheet_name)
                if sheet and addr in sheet.dependents:
                    for dep in sheet.dependents[addr]:
                        if dep in nodes:
                            visit(dep)
                result.append(node)

        for node in nodes:
            visit(node)

        return result[::-1]
