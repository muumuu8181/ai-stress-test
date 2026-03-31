# TOML Parser & Writer

A TOML v1.0 compliant parser and writer implemented using only the Python standard library.

## Features

- TOML v1.0 compliant.
- Supports all TOML data types: String, Integer, Float, Boolean, Datetime, Array, and Inline Table.
- Supports Tables and Array of Tables.
- Handles dotted keys.
- Duplicate key detection and other validations.
- Supports multi-line strings and literal strings.

## Installation

This is a standalone package. You can copy the `tomlparser` directory into your project.

## Usage

```python
from tomlparser import loads, dumps

# Parse TOML string
toml_str = """
title = "TOML Example"
[owner]
name = "Tom Preston-Werner"
dob = 1979-05-27T07:32:00Z
"""
data = loads(toml_str)
print(data['owner']['name'])  # Output: Tom Preston-Werner

# Dump dictionary to TOML string
new_toml_str = dumps(data)
print(new_toml_str)
```

## License

MIT
