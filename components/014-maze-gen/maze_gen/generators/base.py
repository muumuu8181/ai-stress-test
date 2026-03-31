from abc import ABC, abstractmethod
from ..maze import Maze

class MazeGenerator(ABC):
    @abstractmethod
    def generate(self, maze: Maze) -> None:
        pass
