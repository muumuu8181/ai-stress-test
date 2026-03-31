from typing import List, Tuple
from .base import MazeSolver
from ..maze import Maze, CellType

class DFSSolver(MazeSolver):
    """
    Depth-First Search (DFS) solver.
    """

    def solve(self, maze: Maze) -> Tuple[List[Tuple[int, int]], int]:
        start = maze.start
        goal = maze.goal

        stack = [(start, [start])]
        visited = {start}
        steps = 0

        while stack:
            (r, c), path = stack.pop()
            steps += 1

            if (r, c) == goal:
                return path, steps

            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if maze.is_within_bounds(nr, nc) and \
                   maze.get_cell(nr, nc) == CellType.PATH and \
                   (nr, nc) not in visited:
                    visited.add((nr, nc))
                    stack.append(((nr, nc), path + [(nr, nc)]))

        return [], steps
