import os
from typing import List, Optional, Tuple
from .board import SudokuBoard
from .solver import SudokuSolver


def suggest_hint(board: SudokuBoard) -> Optional[Tuple[int, int, int]]:
    """
    Suggests the next move (row, col, value).
    It tries to find a cell with only one possible candidate (naked single).
    """
    if board.is_solved():
        return None

    grid = board.to_list()
    solver = SudokuSolver(board)

    # Check for naked singles first
    for r in range(SudokuBoard.SIZE):
        for c in range(SudokuBoard.SIZE):
            if grid[r][c] == 0:
                candidates = solver._get_candidates(grid, r, c)
                if len(candidates) == 1:
                    return r, c, candidates.pop()

    # If no naked singles, get the solution and pick a cell
    solution = solver.solve()
    if solution:
        for r in range(SudokuBoard.SIZE):
            for c in range(SudokuBoard.SIZE):
                if grid[r][c] == 0:
                    return r, c, solution.get(r, c)

    return None


def load_from_file(filepath: str) -> SudokuBoard:
    """Loads a Sudoku board from a text file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, 'r') as f:
        content = f.read().splitlines()

    grid = []
    for line in content:
        # Strip comments and handle various separators
        line = line.split('#')[0].strip()
        if not line:
            continue

        # Numbers can be separated by spaces, commas, etc.
        # We replace non-numeric characters with spaces
        nums_str = ''.join([c if c.isdigit() or c == '.' else ' ' for c in line]).split()
        row = [int(n) if n != '.' else 0 for n in nums_str]

        if row:
            if len(row) != SudokuBoard.SIZE:
                raise ValueError(f"Invalid row length: {len(row)}")
            grid.append(row)

    if len(grid) != SudokuBoard.SIZE:
        raise ValueError(f"Invalid number of rows: {len(grid)}")

    return SudokuBoard(grid)


def save_to_file(board: SudokuBoard, filepath: str) -> None:
    """Saves the Sudoku board to a text file."""
    with open(filepath, 'w') as f:
        grid = board.to_list()
        for row in grid:
            f.write(' '.join(str(n) if n != 0 else '.' for n in row) + '\n')
