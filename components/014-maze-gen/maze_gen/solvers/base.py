from abc import ABC, abstractmethod
from typing import List, Tuple
from ..maze import Maze

class MazeSolver(ABC):
    @abstractmethod
    def solve(self, maze: Maze) -> Tuple[List[Tuple[int, int]], int]:
        """
        Solve the maze.
        Returns:
            - List[Tuple[int, int]]: The path from start to goal.
            - int: The number of steps taken.
        """
        pass
