from typing import List, Optional, Set, Tuple


class SudokuBoard:
    """
    Represents a 9x9 Sudoku board.
    """

    SIZE = 9
    SUBGRID_SIZE = 3

    def __init__(self, board: Optional[List[List[int]]] = None) -> None:
        """
        Initializes the Sudoku board.

        Args:
            board: A 9x9 list of lists of integers. 0 represents an empty cell.
                   If None, an empty board is created.
        """
        if board is None:
            self.grid = [[0 for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        else:
            if len(board) != self.SIZE or any(len(row) != self.SIZE for row in board):
                raise ValueError(f"Board must be {self.SIZE}x{self.SIZE}")
            self.grid = [row[:] for row in board]

    def get(self, row: int, col: int) -> int:
        """Gets the value at the specified cell."""
        return self.grid[row][col]

    def set(self, row: int, col: int, value: int) -> None:
        """Sets the value at the specified cell."""
        if not (0 <= value <= 9):
            raise ValueError("Value must be between 0 and 9")
        self.grid[row][col] = value

    def is_valid(self) -> bool:
        """
        Checks if the current board state is valid according to Sudoku rules.
        Does not check if it's solvable, just if there are no conflicts.
        """
        # Check rows
        for row in range(self.SIZE):
            if not self._is_unit_valid(self.grid[row]):
                return False

        # Check columns
        for col in range(self.SIZE):
            column = [self.grid[row][col] for row in range(self.SIZE)]
            if not self._is_unit_valid(column):
                return False

        # Check subgrids
        for r in range(0, self.SIZE, self.SUBGRID_SIZE):
            for c in range(0, self.SIZE, self.SUBGRID_SIZE):
                subgrid = []
                for i in range(self.SUBGRID_SIZE):
                    for j in range(self.SUBGRID_SIZE):
                        subgrid.append(self.grid[r + i][c + j])
                if not self._is_unit_valid(subgrid):
                    return False

        return True

    def _is_unit_valid(self, unit: List[int]) -> bool:
        """Checks if a unit (row, column, or subgrid) has no duplicate non-zero values."""
        nums = [n for n in unit if n != 0]
        return len(nums) == len(set(nums))

    def is_solved(self) -> bool:
        """Checks if the board is completely and correctly solved."""
        if any(0 in row for row in self.grid):
            return False
        return self.is_valid()

    def get_empty_cells(self) -> List[Tuple[int, int]]:
        """Returns a list of (row, col) for all empty cells."""
        return [(r, c) for r in range(self.SIZE) for c in range(self.SIZE) if self.grid[r][c] == 0]

    def copy(self) -> 'SudokuBoard':
        """Returns a deep copy of the board."""
        return SudokuBoard(self.grid)

    def __str__(self) -> str:
        """Returns a pretty-print string representation of the board."""
        lines = []
        for i in range(self.SIZE):
            if i % 3 == 0 and i != 0:
                lines.append("-" * 21)

            row_str = []
            for j in range(self.SIZE):
                if j % 3 == 0 and j != 0:
                    row_str.append("|")
                val = self.grid[i][j]
                row_str.append(str(val) if val != 0 else ".")
            lines.append(" ".join(row_str))
        return "\n".join(lines)

    def to_list(self) -> List[List[int]]:
        """Returns the board as a list of lists."""
        return [row[:] for row in self.grid]
