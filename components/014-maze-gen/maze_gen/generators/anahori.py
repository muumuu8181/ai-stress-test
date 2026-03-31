import random
from .base import MazeGenerator
from ..maze import Maze, CellType

class AnahoriGenerator(MazeGenerator):
    """
    Digging method (穴掘り法).
    1. Fill grid with walls.
    2. Pick a random cell (r, c) where r, c are odd.
    3. Dig (set to PATH) the current cell.
    4. Choose a random neighbor that is 2 steps away.
    5. If the neighbor is within bounds and is a wall, dig the cell between current and neighbor,
       and then move to the neighbor and repeat from step 3.
    6. If all neighbors are explored, backtrack.
    """

    def generate(self, maze: Maze) -> None:
        # Fill grid with walls
        for r in range(maze.grid_height):
            for c in range(maze.grid_width):
                maze.set_cell(r, c, CellType.WALL)

        # Pick random starting cell (odd coordinates)
        start_r = random.randrange(1, maze.grid_height - 1, 2)
        start_c = random.randrange(1, maze.grid_width - 1, 2)

        self._dig(maze, start_r, start_c)

    def _dig(self, maze: Maze, r: int, c: int) -> None:
        maze.set_cell(r, c, CellType.PATH)

        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < maze.grid_height - 1 and 0 < nc < maze.grid_width - 1:
                if maze.get_cell(nr, nc) == CellType.WALL:
                    maze.set_cell(r + dr // 2, c + dc // 2, CellType.PATH)
                    self._dig(maze, nr, nc)
