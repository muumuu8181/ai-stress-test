# Sudoku Solver & Generator

A robust Sudoku solver and generator built with Python's standard library.

## Features

- **Backtracking Solver**: Uses constraint propagation (naked singles) and the Minimum Remaining Values (MRV) heuristic for high performance.
- **Puzzle Generation**: Generates valid Sudoku puzzles with specified difficulty levels: `easy`, `medium`, `hard`, and `expert`. All generated puzzles are guaranteed to have a unique solution.
- **Solution Enumeration**: Supports finding all solutions (up to a limit) for a given puzzle.
- **Hint System**: Suggests the next move based on logical deduction or the overall solution.
- **Validation**: Checks if a board state is valid or if it is completely and correctly solved.
- **Pretty Printing**: Displays the Sudoku board in a readable text format.
- **File I/O**: Loads and saves puzzles from/to simple text files.

## Installation

No external dependencies are required. Just ensure you have Python 3.7+ installed.

## CLI Usage

Run the component as a module from the root directory:

```bash
cd components/013-sudoku-solver
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
```

### Generate a Puzzle

```bash
python3 -m sudoku.cli generate --difficulty hard --output puzzle.txt
```

### Solve a Puzzle

```bash
python3 -m sudoku.cli solve puzzle.txt --output solution.txt
```

### Get a Hint

```bash
python3 -m sudoku.cli hint puzzle.txt
```

## API Usage

```python
from sudoku.board import SudokuBoard
from sudoku.solver import SudokuSolver
from sudoku.generator import SudokuGenerator
from sudoku.utils import suggest_hint

# Generate a puzzle
generator = SudokuGenerator()
board = generator.generate("medium")
print(board)

# Solve a puzzle
solver = SudokuSolver(board)
solution = solver.solve()
if solution:
    print("Solved Board:")
    print(solution)

# Get a hint
hint = suggest_hint(board)
if hint:
    r, c, val = hint
    print(f"Hint: Put {val} at ({r+1}, {c+1})")
```

## Testing

Run tests using `pytest`:

```bash
cd components/013-sudoku-solver
PYTHONPATH=src pytest tests/
```
