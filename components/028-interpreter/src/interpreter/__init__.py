from .lexer import Lexer
from .parser import Parser
from .evaluator import Evaluator

def run(source: str):
    """Executes the source code."""
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()

    parser = Parser(tokens)
    statements = parser.parse()

    evaluator = Evaluator()
    evaluator.interpret(statements)
