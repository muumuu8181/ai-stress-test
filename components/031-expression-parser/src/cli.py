from .evaluator import Environment, Evaluator
from .parser import Parser


def main():
    """
    The main entry point for the interactive REPL.
    """
    print("Mathematical Expression Parser & Evaluator REPL")
    print("Type 'exit' or 'quit' to exit.")

    env = Environment()
    evaluator = Evaluator(env)

    while True:
        try:
            line = input(">>> ")
            if line.strip().lower() in ("exit", "quit"):
                break
            if not line.strip():
                continue

            parser = Parser(line)
            ast = parser.parse()
            result = evaluator.evaluate(ast)
            print(result)

        except EOFError:
            print()
            break
        except (ValueError, SyntaxError, LookupError, ZeroDivisionError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
