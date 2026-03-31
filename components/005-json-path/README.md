# JSONPath Query Engine

A lightweight JSONPath query engine implemented using only the Python standard library.

## Features

- **Basic Paths**: `$.store.book[0].title`
- **Array Indexing**: `[0]`, `[-1]`
- **Array Slicing**: `[0:5]`, `[:3]`, `[::2]`
- **Wildcards**: `$.store.book[*].author`, `$.*`
- **Recursive Descent**: `$..author`
- **Filters**: `$.store.book[?(@.price < 10)]`
- **Multiple Selectors (Union)**: `$['store', 'office']`
- **Script Support**: `[?(@.length > 5)]` (works for strings and arrays)
- **Results Update**: Modify values matching a path.
- **Results Deletion**: Remove values matching a path.

## Installation

No external dependencies required. Simply include the `src/jsonpath` directory in your project.

## Usage

### Finding Values

```python
from jsonpath import find

data = {
    "store": {
        "book": [
            {"title": "Book 1", "price": 5},
            {"title": "Book 2", "price": 15}
        ]
    }
}

# Find all book titles
titles = find(data, "$.store.book[*].title")
# Output: ['Book 1', 'Book 2']

# Find books cheaper than 10
cheap_books = find(data, "$.store.book[?(@.price < 10)]")
# Output: [{'title': 'Book 1', 'price': 5}]
```

### Updating Values

```python
from jsonpath import update

data = {"a": 1, "b": 2}
update(data, "$.a", 10)
# data is now {"a": 10, "b": 2}
```

### Deleting Values

```python
from jsonpath import delete

data = {"a": 1, "b": 2}
delete(data, "$.b")
# data is now {"a": 1}
```

## Running Tests

```bash
PYTHONPATH=src pytest tests
```
