import sys
import argparse
from . import run

def main():
    """Main entry point for the interpreter CLI."""
    parser = argparse.ArgumentParser(description="Simple Programming Language Interpreter")
    parser.add_argument("file", help="The source file to execute")
    args = parser.parse_args()

    try:
        with open(args.file, "r") as f:
            source = f.read()
        run(source)
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
