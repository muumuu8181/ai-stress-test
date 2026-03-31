from typing import List, Optional, Any, Dict, Set
from .command import Command

class HistoryNode:
    """
    A node in the history tree, representing an executed command.
    """
    def __init__(self, command: Optional[Command], parent: Optional["HistoryNode"] = None):
        self.command = command
        self.parent = parent
        self.children: List["HistoryNode"] = []
        # Index of the most recently active child to follow when redoing
        self.active_child_index: int = -1

    def add_child(self, node: "HistoryNode") -> None:
        """Adds a child node and sets it as the active child."""
        self.children.append(node)
        self.active_child_index = len(self.children) - 1

class UndoManager:
    """
    Manages a history of commands with undo/redo capabilities and support for branching.
    """
    def __init__(self, max_commands: Optional[int] = None):
        """
        Initializes the UndoManager.

        Args:
            max_commands: The maximum number of commands to store in history.
                          When this limit is reached, the oldest commands are removed.
                          None means no limit.
        """
        self.root = HistoryNode(None)  # Dummy root node
        self.current_node = self.root
        self.max_commands = max_commands
        self.total_nodes = 0

    def execute(self, command: Command) -> None:
        """
        Executes a command and adds it to the history.
        If there are any redoable commands, executing a new command creates a new branch.

        Args:
            command: The command to execute.
        """
        # Check if we can merge with the current command
        if self.current_node != self.root and not self.current_node.children:
            # Merging is only allowed if there are no redo branches from the current node
            if self.current_node.command.can_merge_with(command):
                merged_command = self.current_node.command.merge_with(command)
                self.current_node.command = merged_command
                command.execute()
                return

        command.execute()
        new_node = HistoryNode(command, parent=self.current_node)
        self.current_node.add_child(new_node)
        self.current_node = new_node
        self.total_nodes += 1

        if self.max_commands is not None and self.total_nodes > self.max_commands:
            self._prune_history()

    def undo(self) -> bool:
        """
        Undoes the most recent command.

        Returns:
            True if a command was undone, False if there's nothing to undo.
        """
        if self.current_node == self.root:
            return False

        self.current_node.command.undo()
        self.current_node = self.current_node.parent
        return True

    def redo(self) -> bool:
        """
        Redoes the next command in the active branch.

        Returns:
            True if a command was redone, False if there's nothing to redo.
        """
        if not self.current_node.children:
            return False

        # Redo the most recently active branch
        next_node = self.current_node.children[self.current_node.active_child_index]
        next_node.command.execute()
        self.current_node = next_node
        return True

    def _prune_history(self) -> None:
        """
        Removes the oldest nodes to keep the history within the memory limit.
        """
        if self.total_nodes <= 0:
            return

        path_to_current = self._get_path_to_current()
        path_list = self._get_path_list_to_current()

        # 1. Try to prune a branch that is not on the path to current_node
        for p_node in path_list:
            target_child_index = -1
            for i, child in enumerate(p_node.children):
                if child not in path_to_current:
                    target_child_index = i
                    break

            if target_child_index != -1:
                pruned_node = p_node.children.pop(target_child_index)
                self.total_nodes -= self._count_nodes(pruned_node)
                # Update active_child_index
                if p_node.active_child_index == target_child_index:
                    p_node.active_child_index = len(p_node.children) - 1
                elif p_node.active_child_index > target_child_index:
                    p_node.active_child_index -= 1
                return

        # 2. If no off-path branches, prune the oldest node on the current path
        # This is the first child of root.
        if self.root.children:
            old_first_node = self.root.children.pop(0)
            # Re-attach its children to root
            for child in old_first_node.children:
                child.parent = self.root
                self.root.children.append(child)

            # Update root's active_child_index to something sensible
            if self.root.children:
                self.root.active_child_index = len(self.root.children) - 1
            else:
                self.root.active_child_index = -1

            self.total_nodes -= 1
            if self.current_node == old_first_node:
                self.current_node = self.root

    def _get_path_to_current(self) -> Set["HistoryNode"]:
        path = set()
        node = self.current_node
        while node:
            path.add(node)
            node = node.parent
        return path

    def _get_path_list_to_current(self) -> List["HistoryNode"]:
        path = []
        node = self.current_node
        while node:
            path.append(node)
            node = node.parent
        return list(reversed(path))

    def _count_nodes(self, node: "HistoryNode") -> int:
        count = 1
        for child in node.children:
            count += self._count_nodes(child)
        return count
