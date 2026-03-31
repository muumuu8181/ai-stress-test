# Undo/Redo Manager

A command-pattern based Undo/Redo manager with support for merging operations, branching history, and memory limits.

## Features

- **Command Pattern**: Encapsulate actions as objects that can be executed and undone.
- **Branching History**: When you undo and then execute a new command, a new branch is created in the history. Redo follows the most recently active branch.
- **Command Merging**: Consecutive similar commands (e.g., character typing) can be merged into a single undoable action to keep history clean.
- **Memory Limit**: Prunes the oldest branches and nodes when a specified limit is reached to manage memory usage.
- **Type-Safe**: Fully typed with Python type hints.

## Installation

No external dependencies required. Requires Python 3.10+.

## Usage

### Defining a Command

```python
from src.command import Command

class AppendCommand(Command):
    def __init__(self, target_list, item):
        self.target_list = target_list
        self.item = item

    def execute(self):
        self.target_list.append(self.item)

    def undo(self):
        self.target_list.pop()
```

### Using the UndoManager

```python
from src.undo_manager import UndoManager

target = []
um = UndoManager(max_commands=100)

# Execute commands
um.execute(AppendCommand(target, "A"))
um.execute(AppendCommand(target, "B"))
print(target) # ["A", "B"]

# Undo
um.undo()
print(target) # ["A"]

# Redo
um.redo()
print(target) # ["A", "B"]

# Branching
um.undo()
um.execute(AppendCommand(target, "C"))
print(target) # ["A", "C"]

# Redo follows the "C" branch
um.undo()
um.redo()
print(target) # ["A", "C"]
```

### Merging Commands

Override `can_merge_with` and `merge_with` in your command class:

```python
class TypeCommand(Command):
    def __init__(self, buffer, char):
        self.buffer = buffer
        self.char = char

    def execute(self):
        self.buffer.append(self.char)

    def undo(self):
        self.buffer.pop()

    def can_merge_with(self, other):
        return isinstance(other, TypeCommand)

    def merge_with(self, other):
        # Return a new command that represents both actions
        return TypeCommand(self.buffer, self.char + other.char)
```

## Running Tests

```bash
pytest tests/
```

## CLI Demonstration

Run the built-in REPL to see the manager in action:

```bash
python3 src/cli.py
```
