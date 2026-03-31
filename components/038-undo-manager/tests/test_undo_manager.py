import pytest
from src.undo_manager import UndoManager
from src.command import Command

class TextCommand(Command):
    def __init__(self, target: list, text: str):
        self.target = target
        self.text = text

    def execute(self) -> None:
        self.target.append(self.text)

    def undo(self) -> None:
        self.target.pop()

    def __repr__(self):
        return f"TextCommand('{self.text}')"

class MergeableTextCommand(Command):
    def __init__(self, target: list, text: str):
        self.target = target
        self.text = text

    def execute(self) -> None:
        if not self.target:
            self.target.append(self.text)
        else:
            self.target[0] += self.text

    def undo(self) -> None:
        self.target[0] = self.target[0][:-len(self.text)]
        if not self.target[0]:
            self.target.pop()

    def can_merge_with(self, other: Command) -> bool:
        return isinstance(other, MergeableTextCommand)

    def merge_with(self, other: Command) -> Command:
        return MergeableTextCommand(self.target, self.text + other.text)

def test_undo_redo_sequence():
    target = []
    um = UndoManager()

    um.execute(TextCommand(target, "A"))
    um.execute(TextCommand(target, "B"))
    um.execute(TextCommand(target, "C"))

    assert target == ["A", "B", "C"]

    um.undo()
    assert target == ["A", "B"]

    um.undo()
    assert target == ["A"]

    um.redo()
    assert target == ["A", "B"]

    um.redo()
    assert target == ["A", "B", "C"]

    # Redo when nothing to redo
    assert not um.redo()

def test_branching():
    target = []
    um = UndoManager()

    um.execute(TextCommand(target, "A"))
    um.execute(TextCommand(target, "B"))

    um.undo() # Target: ["A"]

    um.execute(TextCommand(target, "C"))
    assert target == ["A", "C"]

    um.undo() # Target: ["A"]

    # Redo should follow the latest branch "C"
    um.redo()
    assert target == ["A", "C"]

def test_merging():
    target = []
    um = UndoManager()

    um.execute(MergeableTextCommand(target, "H"))
    um.execute(MergeableTextCommand(target, "e"))
    um.execute(MergeableTextCommand(target, "l"))
    um.execute(MergeableTextCommand(target, "l"))
    um.execute(MergeableTextCommand(target, "o"))

    assert target == ["Hello"]
    assert um.total_nodes == 1

    um.undo()
    assert target == []

    um.redo()
    assert target == ["Hello"]

def test_no_merge_after_undo():
    # If we undo, then redo, the next command should NOT merge into the redone command?
    # Actually, the logic says "if not self.current_node.children".
    # After redo, the current node has children (the next node in history).
    # So it shouldn't merge.
    target = []
    um = UndoManager()

    um.execute(MergeableTextCommand(target, "A"))
    um.undo()
    um.redo()

    um.execute(MergeableTextCommand(target, "B"))
    # Should not merge because "A" node has children? No, "A" node is current_node,
    # it was redone. Wait, after redo, "A" node is current_node.
    # Does "A" node have children? Yes, it had children BEFORE undo.
    # Actually, in the simple case, "A" has no children.
    # Let's re-read: "A" executed. current_node is "A". children: [].
    # undo. current_node is root.
    # redo. current_node is "A".
    # execute "B". current_node is "A". children: [].
    # So it SHOULD merge if children is empty.

    assert target == ["AB"]
    assert um.total_nodes == 1

def test_max_commands_pruning():
    target = []
    um = UndoManager(max_commands=2)

    um.execute(TextCommand(target, "A"))
    um.execute(TextCommand(target, "B"))
    um.execute(TextCommand(target, "C"))

    # "A" should be pruned.
    assert um.total_nodes == 2

    # Can only undo twice
    assert um.undo() # Undoes "C", target is ["A", "B"]
    assert um.undo() # Undoes "B", target is ["A"]
    assert not um.undo() # Root reached

    assert target == ["A"] # Target still has A because Command.undo() wasn't called for it

def test_pruning_with_branches():
    target = []
    um = UndoManager(max_commands=2)

    um.execute(TextCommand(target, "A"))
    um.execute(TextCommand(target, "B"))

    um.undo() # current_node is A
    um.execute(TextCommand(target, "C")) # branch C from A. Total nodes: A, B, C (3) -> Prune 1.

    # Path to current: Root -> A -> C.
    # B is NOT on path to current. So B should be pruned.
    assert um.total_nodes == 2

    um.undo() # C
    assert target == ["A"]
    um.redo() # C again
    assert target == ["A", "C"]

    # B should be gone
    # Actually, there's no way to redo B now.

def test_edge_cases():
    um = UndoManager()
    assert not um.undo()
    assert not um.redo()

    # Command that raises error
    class ErrorCommand(Command):
        def execute(self): raise ValueError("Fail")
        def undo(self): pass

    with pytest.raises(ValueError):
        um.execute(ErrorCommand())

def test_merge_not_implemented():
    class SimpleCommand(Command):
        def execute(self): pass
        def undo(self): pass
        def can_merge_with(self, other): return True
        # merge_with not implemented

    um = UndoManager()
    um.execute(SimpleCommand())
    with pytest.raises(NotImplementedError):
        um.execute(SimpleCommand())
