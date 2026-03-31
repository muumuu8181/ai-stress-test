import pytest
from src.undo_manager import UndoManager, HistoryNode
from src.command import Command

class SimpleCommand(Command):
    def execute(self): pass
    def undo(self): pass

def test_pruning_multiple_branches():
    um = UndoManager(max_commands=5)
    # Root
    #  -> A (1)
    #     -> B (2)
    #     -> C (3)
    um.execute(SimpleCommand()) # A
    node_a = um.current_node
    um.execute(SimpleCommand()) # B
    um.undo()
    um.execute(SimpleCommand()) # C

    # Current path: Root -> A -> C
    # Branch B is not on current path.

    # Add more nodes to force pruning
    um.execute(SimpleCommand()) # D (4)
    um.execute(SimpleCommand()) # E (5)

    assert um.total_nodes == 5

    # Next execute should prune B
    um.execute(SimpleCommand()) # F (6 -> 5)
    assert um.total_nodes == 5

    # Check if B is pruned. B was a child of A.
    assert len(node_a.children) == 1
    assert node_a.children[0].command != None # It should be C

def test_history_node_initialization():
    node = HistoryNode(None)
    assert node.command is None
    assert node.parent is None
    assert node.children == []
    assert node.active_child_index == -1

def test_prune_with_no_children():
    um = UndoManager(max_commands=1)
    # This shouldn't really happen if total_nodes > 0, but for coverage:
    um.root.children = []
    um._prune_history() # Should just return
    assert um.total_nodes == 0

def test_pruning_active_child_index_update():
    um = UndoManager(max_commands=5)
    um.execute(SimpleCommand()) # A
    um.execute(SimpleCommand()) # B
    um.undo() # Current: A

    # Force A to have B and C
    um.execute(SimpleCommand()) # C. A has children [B, C]. Active is C (index 1).
    node_a = um.root.children[0]
    assert node_a.active_child_index == 1

    # Add nodes to force prune
    um.execute(SimpleCommand()) # D (4)
    um.execute(SimpleCommand()) # E (5)
    um.execute(SimpleCommand()) # F (6 -> 5)

    # B was at 0, it should be pruned.
    assert node_a.active_child_index == 0
    assert len(node_a.children) == 1
    assert node_a.children[0].command is not None # C
