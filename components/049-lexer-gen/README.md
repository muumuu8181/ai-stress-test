# Lexer Generator

A tool to generate a lexer in Python from a DSL.

## Features

- Define tokens with names and regex patterns.
- Specify priority by order of definition.
- Automatic line and column tracking.
- Skip whitespace and comments.
- Support for multiline tokens.
- Error recovery (skipping invalid characters).
- Python code generation for the lexer.
- Unicode support.
- Custom actions for tokens.

## DSL Format

```
%skip /pattern/        # Define a pattern to skip (e.g. whitespace)

TOKEN_NAME: /pattern/  # Define a token
```

## Usage

```python
from lexer_gen.generator import LexerGenerator

gen = LexerGenerator()
gen.add_skip(r'[ \t\r\n]+')
gen.add_skip(r'//.*')
gen.add_token('NUMBER', r'\d+')
gen.add_token('PLUS', r'\+')
gen.add_token('MINUS', r'-')

# Generate code
code = gen.generate(class_name='MyLexer')
with open('my_lexer.py', 'w') as f:
    f.write(code)
```

## Generated Lexer Usage

```python
from my_lexer import MyLexer

lexer = MyLexer("123 + 456")
for token in lexer.tokenize():
    print(token)
```
