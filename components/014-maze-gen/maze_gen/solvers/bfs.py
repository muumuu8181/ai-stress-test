from collections import deque
from typing import List, Tuple
from .base import MazeSolver
from ..maze import Maze, CellType

class BFSSolver(MazeSolver):
    """
    Breadth-First Search (BFS) solver.
    Guarantees the shortest path in an unweighted grid.
    """

    def solve(self, maze: Maze) -> Tuple[List[Tuple[int, int]], int]:
        start = maze.start
        goal = maze.goal

        queue = deque([(start, [start])])
        visited = {start}
        steps = 0

        while queue:
            (r, c), path = queue.popleft()
            steps += 1

            if (r, c) == goal:
                return path, steps

            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if maze.is_within_bounds(nr, nc) and \
                   maze.get_cell(nr, nc) == CellType.PATH and \
                   (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append(((nr, nc), path + [(nr, nc)]))

        return [], steps
