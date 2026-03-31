import random
from .base import MazeGenerator
from ..maze import Maze, CellType

class BoutaoshiGenerator(MazeGenerator):
    """
    Stick-down method (棒倒し法).
    1. Grid dimensions must be odd.
    2. Surround the entire grid with walls.
    3. Place walls at (2i, 2j) for i=1 to height, j=1 to width.
    4. For each wall at (2i, 2j), knock it down in one of four directions (up, down, left, right)
       to create a new wall. For the first row of walls, four directions are allowed.
       For other rows, only three directions (down, left, right) are allowed to avoid duplicates.
    """

    def generate(self, maze: Maze) -> None:
        # Initialize grid with paths and surrounding walls
        for r in range(maze.grid_height):
            for c in range(maze.grid_width):
                if r == 0 or r == maze.grid_height - 1 or c == 0 or c == maze.grid_width - 1:
                    maze.set_cell(r, c, CellType.WALL)
                else:
                    maze.set_cell(r, c, CellType.PATH)

        # Place sticks and fall them
        for r in range(2, maze.grid_height - 1, 2):
            for c in range(2, maze.grid_width - 1, 2):
                maze.set_cell(r, c, CellType.WALL)

                # Directions: (dr, dc)
                directions = [(0, 1), (1, 0), (0, -1)]  # right, down, left
                if r == 2:
                    directions.append((-1, 0))  # up (only for the first row)

                while True:
                    dr, dc = random.choice(directions)
                    nr, nc = r + dr, c + dc
                    if maze.get_cell(nr, nc) == CellType.PATH:
                        maze.set_cell(nr, nc, CellType.WALL)
                        break
