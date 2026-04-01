import os
from sudoku.board import SudokuBoard
from sudoku.utils import load_from_file, save_to_file, suggest_hint


def test_file_io(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    p = d / "test.txt"

    board = SudokuBoard()
    board.set(0, 0, 5)
    save_to_file(board, str(p))

    loaded_board = load_from_file(str(p))
    assert loaded_board.get(0, 0) == 5


def test_suggest_hint():
    grid = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    board = SudokuBoard(grid)
    hint = suggest_hint(board)
    assert hint is not None
    r, c, val = hint
    assert board.get(r, c) == 0
    # In this specific easy board,
    # for grid[0][2], candidates are {4} because:
    # 5,3 are in row
    # 8,4 are in subgrid (but 8 is already in board at [2][2])
    # 4 is NOT in row or col 2
    # Let's check a more certain cell

    # After solving, checking with another cell
    from sudoku.solver import SudokuSolver
    solver = SudokuSolver(board)
    solution = solver.solve()
    assert solution is not None
    assert solution.get(r, c) == val
