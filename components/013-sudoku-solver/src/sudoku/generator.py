import random
from typing import Optional, List, Tuple
from .board import SudokuBoard
from .solver import SudokuSolver


class SudokuGenerator:
    """
    Sudoku puzzle generator with difficulty levels.
    """

    DIFFICULTIES = {
        "easy": 35,    # Number of clues
        "medium": 30,
        "hard": 25,
        "expert": 20
    }

    def generate(self, difficulty: str = "medium") -> SudokuBoard:
        """
        Generates a Sudoku puzzle with the given difficulty.
        """
        if difficulty not in self.DIFFICULTIES:
            raise ValueError(f"Invalid difficulty: {difficulty}")

        # 1. Generate a full valid board
        board = self._generate_full_board()

        # 2. Remove numbers while ensuring uniqueness
        clues_target = self.DIFFICULTIES[difficulty]
        return self._remove_numbers(board, clues_target)

    def _generate_full_board(self) -> SudokuBoard:
        """Generates a complete, valid Sudoku board."""
        board = SudokuBoard()
        grid = board.to_list()
        self._fill_recursive(grid)
        return SudokuBoard(grid)

    def _fill_recursive(self, grid: List[List[int]]) -> bool:
        """Fills the grid using backtracking and random selection."""
        for r in range(SudokuBoard.SIZE):
            for c in range(SudokuBoard.SIZE):
                if grid[r][c] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for val in nums:
                        if self._is_safe(grid, r, c, val):
                            grid[r][c] = val
                            if self._fill_recursive(grid):
                                return True
                            grid[r][c] = 0
                    return False
        return True

    def _is_safe(self, grid: List[List[int]], row: int, col: int, val: int) -> bool:
        """Checks if placing val at (row, col) is valid."""
        for i in range(SudokuBoard.SIZE):
            if grid[row][i] == val or grid[i][col] == val:
                return False

        start_row, start_col = (row // 3) * 3, (col // 3) * 3
        for i in range(3):
            for j in range(3):
                if grid[start_row + i][start_col + j] == val:
                    return False
        return True

    def _remove_numbers(self, board: SudokuBoard, target_clues: int) -> SudokuBoard:
        """Removes numbers from a full board to create a puzzle with a unique solution."""
        grid = board.to_list()
        cells = [(r, c) for r in range(SudokuBoard.SIZE) for c in range(SudokuBoard.SIZE)]
        random.shuffle(cells)

        clues_count = SudokuBoard.SIZE * SudokuBoard.SIZE

        for r, c in cells:
            if clues_count <= target_clues:
                break

            temp = grid[r][c]
            grid[r][c] = 0

            solver = SudokuSolver(SudokuBoard(grid))
            if solver.has_unique_solution():
                clues_count -= 1
            else:
                grid[r][c] = temp

        return SudokuBoard(grid)
