from typing import List, Tuple, Optional
import enum

class CellType(enum.IntEnum):
    WALL = 1
    PATH = 0

class Maze:
    """
    A class to represent a maze.
    The maze is represented by a 2D grid where (2*height + 1) x (2*width + 1)
    to account for walls and cells.
    """

    def __init__(self, width: int, height: int):
        """
        Initialize a maze with given dimensions.
        :param width: Number of cells in width.
        :param height: Number of cells in height.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Maze dimensions must be positive integers.")

        self.width = width
        self.height = height
        self.grid_width = 2 * width + 1
        self.grid_height = 2 * height + 1
        self.grid = [[CellType.WALL for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.start: Tuple[int, int] = (1, 1)
        self.goal: Tuple[int, int] = (self.grid_height - 2, self.grid_width - 2)

    def set_cell(self, r: int, c: int, cell_type: CellType) -> None:
        """Set the cell type at (r, c)."""
        self.grid[r][c] = cell_type

    def get_cell(self, r: int, c: int) -> CellType:
        """Get the cell type at (r, c)."""
        return self.grid[r][c]

    def is_within_bounds(self, r: int, c: int) -> bool:
        """Check if the given (r, c) is within the grid bounds."""
        return 0 <= r < self.grid_height and 0 <= c < self.grid_width

    def set_start(self, r: int, c: int) -> None:
        """Set the start position."""
        if not self.is_within_bounds(r, c):
            raise ValueError("Start position out of bounds.")
        self.start = (r, c)

    def set_goal(self, r: int, c: int) -> None:
        """Set the goal position."""
        if not self.is_within_bounds(r, c):
            raise ValueError("Goal position out of bounds.")
        self.goal = (r, c)

    def to_dict(self) -> dict:
        """Convert maze to dictionary for serialization."""
        return {
            "width": self.width,
            "height": self.height,
            "grid": [[int(cell) for cell in row] for row in self.grid],
            "start": self.start,
            "goal": self.goal
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Maze':
        """Create a maze from a dictionary."""
        maze = cls(data["width"], data["height"])
        maze.grid = [[CellType(cell) for cell in row] for row in data["grid"]]
        maze.start = tuple(data["start"])
        maze.goal = tuple(data["goal"])
        return maze
