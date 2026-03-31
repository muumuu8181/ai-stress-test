# Simple Programming Language Interpreter

A simple, tree-walk interpreter for a custom programming language implemented in Python.

## Language Specification

### Variables
```
let x = 10
let name = "Jules"
let is_valid = true
```

### Types
- Integer: `10`, `-5`
- Float: `3.14`, `-0.5`
- String: `"hello"`, `'world'`
- Boolean: `true`, `false`
- Array: `[1, 2, 3]`, `["a", "b"]`

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `and`, `or`, `not`

### Control Structures
#### If-elif-else
```
if x > 10 {
  print("Large")
} elif x > 5 {
  print("Medium")
} else {
  print("Small")
}
```

#### Loops
```
while x > 0 {
  x = x - 1
}

for item in [1, 2, 3] {
  print(item)
}
```

### Functions
```
fn add(a, b) {
  let res = a + b
  print(res)
}

add(10, 20)
```

### Built-in Functions
- `print(...)`: Prints values to standard output.
- `len(obj)`: Returns the length of a string or array.
- `type(obj)`: Returns the type name as a string.
- `push(array, element)`: Appends an element to an array.
- `pop(array)`: Removes and returns the last element of an array.

## Usage

### Run from CLI
```bash
python3 -m components.028-interpreter.src.interpreter your_script.txt
```

### Run from Code
```python
from components["028-interpreter"].src.interpreter import run

source = """
let x = 10
print("The value is", x)
"""
run(source)
```

## Implementation Details
- **Lexer**: Scans source code into tokens.
- **Parser**: Recursive descent parser that builds an AST.
- **Evaluator**: Evaluates the AST using an environment-based scope management system.
