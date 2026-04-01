from sudoku.generator import SudokuGenerator
from sudoku.solver import SudokuSolver


def test_generate_easy():
    generator = SudokuGenerator()
    board = generator.generate("easy")
    assert board is not None
    assert board.is_valid()

    # Check clues count
    clues = 81 - len(board.get_empty_cells())
    # Easy target is 35 clues. Our implementation removes numbers while unique solution is maintained.
    # It should be at least target or slightly more if removals would break uniqueness.
    # Actually, it stops when target_clues is reached OR it can't remove more.
    assert clues >= 35


def test_uniqueness():
    generator = SudokuGenerator()
    board = generator.generate("medium")
    solver = SudokuSolver(board)
    assert solver.has_unique_solution()


def test_expert_is_harder():
    generator = SudokuGenerator()
    board_easy = generator.generate("easy")
    board_expert = generator.generate("expert")

    clues_easy = 81 - len(board_easy.get_empty_cells())
    clues_expert = 81 - len(board_expert.get_empty_cells())

    assert clues_easy > clues_expert
