from typing import List, Optional, Set, Dict, Tuple
from .board import SudokuBoard


class SudokuSolver:
    """
    Sudoku solver using constraint propagation and backtracking.
    """

    def __init__(self, board: SudokuBoard) -> None:
        self.board = board.copy()
        self.size = SudokuBoard.SIZE
        self.subgrid_size = SudokuBoard.SUBGRID_SIZE

    def solve(self) -> Optional[SudokuBoard]:
        """
        Finds a single solution for the Sudoku puzzle.
        Returns the solved board or None if no solution exists.
        """
        solutions = self._solve_recursive(self.board.to_list(), limit=1)
        if solutions:
            return SudokuBoard(solutions[0])
        return None

    def solve_all(self, limit: int = 100) -> List[SudokuBoard]:
        """
        Enumerates all solutions for the Sudoku puzzle up to a limit.
        """
        solutions = self._solve_recursive(self.board.to_list(), limit=limit)
        return [SudokuBoard(sol) for sol in solutions]

    def has_unique_solution(self) -> bool:
        """Checks if the puzzle has exactly one solution."""
        solutions = self._solve_recursive(self.board.to_list(), limit=2)
        return len(solutions) == 1

    def _solve_recursive(self, grid: List[List[int]], limit: int) -> List[List[List[int]]]:
        """
        Recursive solver with constraint propagation (naked singles) and backtracking.
        """
        solutions: List[List[List[int]]] = []

        # Initial constraint propagation
        if not self._propagate_constraints(grid):
            return []

        self._backtrack(grid, solutions, limit)
        return solutions

    def _propagate_constraints(self, grid: List[List[int]]) -> bool:
        """
        Repeatedly find and fill cells with only one possible value (naked singles).
        Returns False if a conflict is detected.
        """
        changed = True
        while changed:
            changed = False
            for r in range(self.size):
                for c in range(self.size):
                    if grid[r][c] == 0:
                        candidates = self._get_candidates(grid, r, c)
                        if not candidates:
                            return False  # No possible value for an empty cell
                        if len(candidates) == 1:
                            grid[r][c] = candidates.pop()
                            changed = True
        return True

    def _get_candidates(self, grid: List[List[int]], row: int, col: int) -> Set[int]:
        """Returns a set of valid candidate values for the given cell."""
        used = 0

        # Row and column
        for i in range(self.size):
            val_row = grid[row][i]
            if val_row: used |= 1 << val_row
            val_col = grid[i][col]
            if val_col: used |= 1 << val_col

        # Subgrid
        start_row, start_col = (row // self.subgrid_size) * self.subgrid_size, (col // self.subgrid_size) * self.subgrid_size
        for i in range(self.subgrid_size):
            r = start_row + i
            for j in range(self.subgrid_size):
                val = grid[r][start_col + j]
                if val: used |= 1 << val

        candidates = set()
        for i in range(1, 10):
            if not (used & (1 << i)):
                candidates.add(i)
        return candidates

    def _backtrack(self, grid: List[List[int]], solutions: List[List[List[int]]], limit: int) -> bool:
        """Backtracking search with simple heuristic (MRV - Minimum Remaining Values)."""
        if len(solutions) >= limit:
            return True

        # Find the empty cell with the fewest candidates (MRV heuristic)
        best_cell: Optional[Tuple[int, int]] = None
        best_candidates: Set[int] = set()

        for r in range(self.size):
            for c in range(self.size):
                if grid[r][c] == 0:
                    candidates = self._get_candidates(grid, r, c)
                    if not candidates:
                        return False # Dead end
                    if best_cell is None or len(candidates) < len(best_candidates):
                        best_cell = (r, c)
                        best_candidates = candidates
                        if len(best_candidates) == 1:
                            break
            if best_candidates and len(best_candidates) == 1:
                break

        if best_cell is None:
            # All cells filled, solution found
            solutions.append([row[:] for row in grid])
            return len(solutions) >= limit

        r, c = best_cell
        for val in sorted(list(best_candidates)):
            grid[r][c] = val
            # Create a copy of the grid for the next branch to avoid complex undo of constraint propagation
            # But constraint propagation is done within each step to speed up search
            next_grid = [row[:] for row in grid]
            if self._propagate_constraints(next_grid):
                if self._backtrack(next_grid, solutions, limit):
                    if len(solutions) >= limit:
                        return True
            grid[r][c] = 0

        return False
