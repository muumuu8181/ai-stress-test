import random
from .base import MazeGenerator
from ..maze import Maze, CellType

class KruskalGenerator(MazeGenerator):
    """
    Randomized Kruskal's algorithm.
    1. Grid dimensions must be odd.
    2. Surround the entire grid with walls.
    3. Initially, every odd-coordinate cell is its own set.
    4. Consider all possible walls between cells as candidates.
    5. Shuffle the candidates.
    6. For each wall (r, c), if it separates cells belonging to different sets, remove the wall (set to PATH)
       and merge the sets.
    """

    def generate(self, maze: Maze) -> None:
        # Initial grid with walls and odd cells as potential paths
        cells = []
        for r in range(1, maze.grid_height - 1, 2):
            for c in range(1, maze.grid_width - 1, 2):
                maze.set_cell(r, c, CellType.PATH)
                cells.append((r, c))

        parent = {(r, c): (r, c) for r in range(1, maze.grid_height - 1, 2) for c in range(1, maze.grid_width - 1, 2)}

        def find(i):
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]

        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j
                return True
            return False

        walls = []
        # Horizontal walls between cells (r, c) and (r, c+2)
        for r in range(1, maze.grid_height - 1, 2):
            for c in range(1, maze.grid_width - 3, 2):
                walls.append(((r, c), (r, c + 2), (r, c + 1)))

        # Vertical walls between cells (r, c) and (r+2, c)
        for r in range(1, maze.grid_height - 3, 2):
            for c in range(1, maze.grid_width - 1, 2):
                walls.append(((r, c), (r + 2, c), (r + 1, c)))

        random.shuffle(walls)

        for cell1, cell2, wall in walls:
            if union(cell1, cell2):
                maze.set_cell(wall[0], wall[1], CellType.PATH)
