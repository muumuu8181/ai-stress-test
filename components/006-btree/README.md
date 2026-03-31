# B-Tree Implementation in Python

A pure Python implementation of the B-Tree data structure with no external dependencies. This implementation supports all basic operations, including insertion, search, and deletion with proper rebalancing.

## Features

- **Standard Operations:** Insertion, Search, and Deletion.
- **Minimum Degree Support:** Specify the minimum degree `t` via the constructor.
- **Range Query:** Retrieve all keys within a specified range `[low, high]`.
- **In-order Traversal:** Supports Python's iterator protocol for in-order traversal.
- **JSON Serialization:** Methods to convert the tree to/from JSON strings for persistence.
- **Debug Tools:** A `dump()` method to visualize the tree structure.
- **Type Safety:** Full type hints and detailed docstrings for all public APIs.

## Installation

This component uses only the Python standard library. Copy `btree.py` to your project and import it.

## Usage

### Basic Operations

```python
from btree import BTree

# Initialize B-Tree with minimum degree t=3
bt = BTree(t=3)

# Insert keys
for key in [10, 20, 5, 6, 12, 30, 7, 17]:
    bt.insert(key)

# Search for a key
result = bt.search(12)
if result:
    node, index = result
    print(f"Found {node.keys[index]} at index {index}")

# Delete a key
bt.delete(12)
```

### Range Query and Iteration

```python
# In-order iteration
for key in bt:
    print(key)

# Range query [7, 20]
keys_in_range = bt.range_query(7, 20)
print(f"Keys between 7 and 20: {keys_in_range}")
```

### Serialization

```python
# Serialize to JSON
json_data = bt.to_json()

# Deserialize from JSON
new_bt = BTree.from_json(json_data)
```

### Debugging

```python
# Print tree structure
print(bt.dump())
```

## Implementation Details

- **Insertion:** Follows the "split full nodes while descending" approach to ensure only one pass down the tree.
- **Deletion:** Implements all cases for B-Tree deletion:
  - Deleting from leaf nodes.
  - Deleting from internal nodes (using predecessors or successors).
  - Rebalancing via borrowing from siblings or merging nodes when they drop below the minimum number of keys (`t-1`).
- **Duplicate Keys:** This implementation allows duplicate keys. They are handled by the standard insertion logic and will appear in-order.

## Testing

Run tests using `pytest`:

```bash
pytest components/006-btree/test_btree.py
```

To check coverage:

```bash
coverage run -m pytest components/006-btree/test_btree.py
coverage report
```
