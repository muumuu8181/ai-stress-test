from abc import ABC, abstractmethod
from typing import Optional

class Command(ABC):
    """
    Abstract base class for all commands.
    A command represents an action that can be executed and undone.
    """

    @abstractmethod
    def execute(self) -> None:
        """
        Executes the command.
        """
        pass

    @abstractmethod
    def undo(self) -> None:
        """
        Undoes the command.
        """
        pass

    def can_merge_with(self, other: "Command") -> bool:
        """
        Checks if this command can be merged with another command.
        By default, commands cannot be merged.

        Args:
            other: The other command to merge with.

        Returns:
            True if the commands can be merged, False otherwise.
        """
        return False

    def merge_with(self, other: "Command") -> "Command":
        """
        Merges this command with another command and returns a new merged command.
        This is typically used to combine consecutive small operations (e.g., typing characters)
        into a single undoable action.

        Args:
            other: The other command to merge with.

        Returns:
            A new Command instance representing the merged action.

        Raises:
            NotImplementedError: If merging is not supported by this command.
        """
        raise NotImplementedError("merge_with is not implemented for this command.")
