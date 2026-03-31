# Simple Template Engine

A Python-based, Jinja-like template engine built with only standard libraries.

## Features

- **Variable Expansion**: `{{ variable }}`, `{{ user.name }}`
- **Conditionals**: `{% if %}`, `{% elif %}`, `{% else %}`, `{% endif %}`
- **Loops**: `{% for item in items %}`, `{% endfor %}`
- **Filters**: `{{ name | upper }}`, `{{ price | currency }}`, `{{ items | join(", ") }}`, `{{ html | safe }}`
- **Inheritance**: `{% extends "base.html" %}`, `{% block content %}`, `{% endblock %}`
- **Comments**: `{# comments are ignored #}`
- **Auto-escaping**: Automatically escapes HTML characters unless the `safe` filter is used.
- **Error Handling**: Detailed error messages with line and column numbers.

## Usage

### Simple Rendering

```python
from templateengine.engine import Environment, Template

env = Environment()
template = Template("Hello, {{ name }}!", env)
print(template.render(name="World"))
# Output: Hello, World!
```

### With Filters

```python
template = Template("Price: {{ price | currency }}", env)
print(template.render(price=19.99))
# Output: Price: $19.99
```

### Template Inheritance

**base.html**
```html
<html>
  <body>
    {% block content %}{% endblock %}
  </body>
</html>
```

**child.html**
```html
{% extends "base.html" %}
{% block content %}
  <h1>Hello World</h1>
{% endblock %}
```

**Rendering**
```python
from templateengine.engine import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("path/to/templates"))
template = env.get_template("child.html")
print(template.render())
```

## Error Reporting

The engine provides helpful error messages for syntax errors or undefined variables:

```python
# NameError: Undefined variable 'unknown' at line 1, column 3
Template("{{ unknown }}", env).render()
```

## Installation

This engine only requires Python 3.12+ and no external dependencies.
To use, simply include the `templateengine` package in your project.

## Testing

Run tests using `pytest`:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
pytest tests/
```
