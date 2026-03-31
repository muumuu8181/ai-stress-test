import random
from .base import MazeGenerator
from ..maze import Maze, CellType

class PrimGenerator(MazeGenerator):
    """
    Randomized Prim's algorithm.
    1. Grid dimensions must be odd.
    2. Start with a random odd-coordinate cell in the maze.
    3. Add its neighbors (2 steps away) to the list of potential cells.
    4. Pick a random neighbor cell from the list.
    5. If the cell is a wall, remove the wall between it and its visited neighbor,
       mark the cell as visited (PATH), and add its neighbors to the list.
    6. Repeat until the list is empty.
    """

    def generate(self, maze: Maze) -> None:
        # Initial grid with walls
        for r in range(maze.grid_height):
            for c in range(maze.grid_width):
                maze.set_cell(r, c, CellType.WALL)

        start_r = random.randrange(1, maze.grid_height - 1, 2)
        start_c = random.randrange(1, maze.grid_width - 1, 2)
        maze.set_cell(start_r, start_c, CellType.PATH)

        # Potential walls to remove
        walls = []
        for dr, dc in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
            nr, nc = start_r + dr, start_c + dc
            if 0 < nr < maze.grid_height - 1 and 0 < nc < maze.grid_width - 1:
                walls.append((nr, nc, start_r + dr // 2, start_c + dc // 2))

        while walls:
            wr, wc, pr, pc = random.choice(walls)
            walls.remove((wr, wc, pr, pc))

            if maze.get_cell(wr, wc) == CellType.WALL:
                maze.set_cell(pr, pc, CellType.PATH)
                maze.set_cell(wr, wc, CellType.PATH)

                for dr, dc in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
                    nr, nc = wr + dr, wc + dc
                    if 0 < nr < maze.grid_height - 1 and 0 < nc < maze.grid_width - 1:
                        if maze.get_cell(nr, nc) == CellType.WALL:
                            walls.append((nr, nc, wr + dr // 2, wc + dc // 2))
