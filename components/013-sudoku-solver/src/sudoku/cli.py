import argparse
import sys
from .board import SudokuBoard
from .solver import SudokuSolver
from .generator import SudokuGenerator
from .utils import load_from_file, save_to_file, suggest_hint


def main():
    parser = argparse.ArgumentParser(description="Sudoku Solver & Generator CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate a Sudoku puzzle")
    gen_parser.add_argument("--difficulty", choices=["easy", "medium", "hard", "expert"], default="medium")
    gen_parser.add_argument("--output", help="Output file path")

    # Solve command
    solve_parser = subparsers.add_parser("solve", help="Solve a Sudoku puzzle")
    solve_parser.add_argument("file", help="Input Sudoku file path")
    solve_parser.add_argument("--all", action="store_true", help="Find all solutions")
    solve_parser.add_argument("--output", help="Output file path")

    # Hint command
    hint_parser = subparsers.add_parser("hint", help="Suggest the next move")
    hint_parser.add_argument("file", help="Input Sudoku file path")

    args = parser.parse_args()

    if args.command == "generate":
        generator = SudokuGenerator()
        board = generator.generate(args.difficulty)
        print(f"Generated {args.difficulty} Sudoku puzzle:")
        print(board)
        if args.output:
            save_to_file(board, args.output)
            print(f"Saved to {args.output}")

    elif args.command == "solve":
        try:
            board = load_from_file(args.file)
            solver = SudokuSolver(board)

            if args.all:
                solutions = solver.solve_all()
                print(f"Found {len(solutions)} solutions.")
                for i, sol in enumerate(solutions):
                    print(f"Solution {i+1}:")
                    print(sol)
                    if args.output and i == 0:
                         save_to_file(sol, args.output)
            else:
                solution = solver.solve()
                if solution:
                    print("Solution found:")
                    print(solution)
                    if args.output:
                        save_to_file(solution, args.output)
                else:
                    print("No solution found.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.command == "hint":
        try:
            board = load_from_file(args.file)
            hint = suggest_hint(board)
            if hint:
                r, c, val = hint
                print(f"Hint: Place {val} at (Row: {r+1}, Col: {c+1})")
            else:
                print("No hint available (already solved or unsolvable).")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
