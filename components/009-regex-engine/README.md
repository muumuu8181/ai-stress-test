# Regex Engine (NFA-based)

A simple regex engine built from scratch in Python using Thompson's NFA construction.

## Features

- **Literal Matching**: `abc`
- **Dot**: `.` (matches any character except newline)
- **Anchors**: `^` (start of string), `$` (end of string)
- **Quantifiers**: `*`, `+`, `?`, `{n,m}`
- **Character Classes**: `[abc]`, `[a-z]`, `[^abc]`, `\d`, `\w`, `\s`
- **Groups**: `(abc)`, capture groups
- **Alternation**: `a|b`
- **Escaping**: `\.`, `\*`, etc.
- **Functions**: `match()`, `search()`, `findall()`, `sub()`

## Usage

```python
from regexengine import match, search, findall, sub

# Match at the beginning of the string
m = match(r"hello (world)", "hello world!")
if m:
    print(m.group(0))  # "hello world"
    print(m.group(1))  # "world"

# Search anywhere in the string
m = search(r"\d+", "The answer is 42.")
if m:
    print(m.group())  # "42"

# Find all occurrences
numbers = findall(r"\d+", "10, 20, 30")
print(numbers)  # ['10', '20', '30']

# Substitute
result = sub(r"(\w+) (\w+)", r"\2 \1", "hello world")
print(result)  # "world hello"

# Use with a callable
def upper(m):
    return m.group().upper()
result = sub(r"\w+", upper, "hello world")
print(result)  # "HELLO WORLD"
```

## Implementation Details

The engine follows these steps:
1. **Lexer**: Tokenizes the regex pattern into a stream of tokens.
2. **Parser**: Converts tokens into an Abstract Syntax Tree (AST) using recursive descent parsing.
3. **NFA Compiler**: Compiles the AST into a Non-deterministic Finite Automaton (NFA) using Thompson's construction.
4. **Matcher/Simulator**: Simulates the NFA using a breadth-first search (BFS) approach, tracking capture group boundaries along each path.

## Quality Standards

- **Tests**: Comprehensive unit and integration tests with >90% coverage.
- **Type Hints**: Fully typed public APIs.
- **Python Version**: Requires Python 3.9+ (uses modern type hints).
