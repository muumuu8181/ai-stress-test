import pytest
from sudoku.board import SudokuBoard


def test_empty_board():
    board = SudokuBoard()
    assert all(all(val == 0 for val in row) for row in board.grid)


def test_board_initialization():
    grid = [[0] * 9 for _ in range(9)]
    grid[0][0] = 5
    board = SudokuBoard(grid)
    assert board.get(0, 0) == 5


def test_invalid_board_size():
    grid = [[0] * 8 for _ in range(9)]
    with pytest.raises(ValueError):
        SudokuBoard(grid)


def test_set_value():
    board = SudokuBoard()
    board.set(0, 0, 5)
    assert board.get(0, 0) == 5
    with pytest.raises(ValueError):
        board.set(0, 0, 10)


def test_is_valid():
    board = SudokuBoard()
    board.set(0, 0, 5)
    board.set(0, 1, 5)  # Duplicate in row
    assert not board.is_valid()

    board.set(0, 1, 6)
    board.set(1, 0, 5)  # Duplicate in column
    assert not board.is_valid()

    board.set(1, 0, 1)
    board.set(1, 1, 5)  # Duplicate in subgrid
    assert not board.is_valid()


def test_is_solved():
    # A known solved Sudoku grid (partially filled)
    grid = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9]
    ]
    board = SudokuBoard(grid)
    assert board.is_solved()


def test_pretty_print():
    board = SudokuBoard()
    board.set(0, 0, 5)
    s = str(board)
    assert "5 . ." in s
    assert "|" in s
    assert "-" in s
