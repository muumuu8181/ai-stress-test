import sys
import os

# Add the component root directory to sys.path
# If this file is in components/038-undo-manager/src/cli.py,
# then os.path.dirname(os.path.abspath(__file__)) is the 'src' directory.
# The parent of that is the component root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.undo_manager import UndoManager
from src.command import Command

class AppendCommand(Command):
    def __init__(self, target_list: list, item: str):
        self.target_list = target_list
        self.item = item

    def execute(self):
        self.target_list.append(self.item)

    def undo(self):
        self.target_list.pop()

    def __repr__(self):
        return f"Append('{self.item}')"

def print_history_tree(node, prefix="", is_last=True, current_node=None):
    marker = ">>> " if node == current_node else "    "
    print(f"{prefix}{'└── ' if is_last else '├── '}{marker}{node.command if node.command else '[ROOT]'}")

    child_prefix = prefix + ("    " if is_last else "│   ")
    for i, child in enumerate(node.children):
        print_history_tree(child, child_prefix, i == len(node.children) - 1, current_node)

def main():
    target = []
    um = UndoManager(max_commands=10)

    print("Undo/Redo Manager REPL")
    print("Commands: add <text>, undo, redo, status, exit")

    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break

        if not line:
            continue

        parts = line.split(None, 1)
        cmd = parts[0].lower()

        if cmd == "exit":
            break
        elif cmd == "add" and len(parts) > 1:
            um.execute(AppendCommand(target, parts[1]))
        elif cmd == "undo":
            if not um.undo():
                print("Nothing to undo.")
        elif cmd == "redo":
            if not um.redo():
                print("Nothing to redo.")
        elif cmd == "status":
            print(f"Current State: {target}")
            print("History Tree:")
            print_history_tree(um.root, current_node=um.current_node)
        else:
            print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
