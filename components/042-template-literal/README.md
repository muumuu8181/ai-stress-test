# Template Literal Engine

A Python-based template engine supporting variable expansion, expression evaluation, conditionals, loops, and filters. Built with only standard libraries.

## Features

- **Variable Expansion**: `${variable}`, `${user.name}`
- **Expression Evaluation**: `${price * quantity}`
- **Filter Pipes**: `${name | upper}`, `${price | currency}`
- **Conditionals**: `{?condition}...{/?}`
- **Loops**: `{@each items as item}...{/each}`
- **HTML Auto-escaping**: Automatically escapes HTML characters unless the `safe` filter is used.
- **Custom Filters**: Register your own filters in the environment.
- **Error Handling**: Detailed error messages with line and column numbers.

## Usage

### Simple Rendering

```python
from templateliteral.engine import Environment

env = Environment()
template = env.from_string("Hello, ${name}!")
print(template.render(name="World"))
# Output: Hello, World!
```

### Expressions and Filters

```python
template = env.from_string("Total: ${price * quantity | currency}")
print(template.render(price=19.99, quantity=3))
# Output: Total: $59.97
```

### Conditionals and Loops

```python
source = """
{?is_admin}
  <h1>Admin Panel</h1>
{/?}
<ul>
  {@each users as user}
    <li>${user.name | upper}</li>
  {/each}
</ul>
"""
template = env.from_string(source)
data = {
    "is_admin": True,
    "users": [{"name": "alice"}, {"name": "bob"}]
}
print(template.render(**data))
```

### Custom Filters

```python
env.register_filter("bold", lambda x: f"<b>{x}</b>")
template = env.from_string("${name | bold | safe}")
print(template.render(name="World"))
# Output: <b>World</b>
```

## Error Reporting

Helpful error messages for syntax errors or expression evaluation errors:

```python
# TemplateSyntaxError: Invalid @each syntax: 'items'. Expected '@each items as item' at line 1, column 1
env.from_string("{@each items}...")
```

## Installation

Requires Python 3.12+.
No external dependencies.

## Testing

Run tests using `pytest`:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pytest tests/
```
