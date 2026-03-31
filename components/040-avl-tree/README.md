# AVL Tree (Self-balancing BST)

An implementation of an AVL Tree in Python, supporting insertion, deletion, searching, merging, and splitting. The tree maintains its balance (height difference of subtrees is at most 1) through rotations.

## Features

- **Insertion**: Automatically balances using LL, RR, LR, RL rotations.
- **Deletion**: Automatically balances after node removal.
- **Search**: Standard BST search.
- **Merge**: Merges another AVL tree into the current one.
- **Split**: Splits the tree into two based on a value.
- **CLI**: Interactive command-line interface for experimentation.

## Installation

This package has no external dependencies except for testing.

```bash
# Clone the repository
cd components/040-avl-tree
```

## Usage

### Programmatic Usage

```python
from src.avl_tree import AVLTree

# Create a tree
tree = AVLTree[int]()

# Insert elements
tree.insert(10)
tree.insert(20)
tree.insert(5)

# Search
node = tree.search(10)
print(node.key)  # Output: 10

# Delete
tree.delete(10)

# Merge
tree2 = AVLTree[int]()
tree2.insert(15)
tree.merge(tree2)

# Split
left_tree, right_tree = tree.split(10)
```

### CLI Usage

You can run the interactive CLI to test the AVL tree:

```bash
python3 src/cli.py
```

Commands:
- `insert <val>`: Insert an integer.
- `delete <val>`: Delete an integer.
- `search <val>`: Search for an integer.
- `print`: Print the tree structure visually.
- `exit`: Exit the CLI.

## Testing

Run tests using `pytest`:

```bash
pytest tests/test_avl_tree.py
```

To check coverage:

```bash
pytest --cov=src tests/
```
