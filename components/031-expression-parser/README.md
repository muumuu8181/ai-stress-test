# Expression Parser & Evaluator

A mathematical expression parser and evaluator that supports arithmetic operations, parentheses, function calls (sin, cos, log), and variable assignments.

## Features

- **Arithmetic Operations**: `+`, `-`, `*`, `/`
- **Parentheses**: `(`, `)` for grouping
- **Functions**: `sin(x)`, `cos(x)`, `log(x)`, `tan(x)`, `sqrt(x)`, `abs(x)`, `exp(x)`
- **Variables**: Assign values to variables using `=` (e.g., `x = 10`)
- **AST Generation**: Separated parsing and evaluation phases.
- **REPL**: Interactive Command Line Interface.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Library

```python
from src.evaluator import Environment, Evaluator
from src.parser import Parser

env = Environment()
parser = Parser("x = 10 * sin(0.5)")
ast = parser.parse()

evaluator = Evaluator(env)
result = evaluator.evaluate(ast)
print(result) # 4.79425538604203
print(env.get("x")) # 4.79425538604203
```

### CLI

```bash
PYTHONPATH=. python3 -m src.cli
```

## Development

### Running Tests

```bash
PYTHONPATH=. python3 -m pytest tests/
```

### Formatting

```bash
black .
isort .
```

### Type Checking

```bash
PYTHONPATH=. mypy src
```
