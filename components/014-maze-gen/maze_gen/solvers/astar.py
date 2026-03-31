import heapq
from typing import List, Tuple
from .base import MazeSolver
from ..maze import Maze, CellType

class AStarSolver(MazeSolver):
    """
    A* search algorithm.
    Uses Manhattan distance as the heuristic.
    """

    def solve(self, maze: Maze) -> Tuple[List[Tuple[int, int]], int]:
        start = maze.start
        goal = maze.goal

        # priority queue stores: (f_score, steps, current_pos, path)
        pq = [(self._heuristic(start, goal), 0, start, [start])]
        visited = {start: 0} # store g_score
        total_steps = 0

        while pq:
            f, g, (r, c), path = heapq.heappop(pq)
            total_steps += 1

            if (r, c) == goal:
                return path, total_steps

            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if maze.is_within_bounds(nr, nc) and \
                   maze.get_cell(nr, nc) == CellType.PATH:
                    new_g = g + 1
                    if (nr, nc) not in visited or new_g < visited[(nr, nc)]:
                        visited[(nr, nc)] = new_g
                        new_f = new_g + self._heuristic((nr, nc), goal)
                        heapq.heappush(pq, (new_f, new_g, (nr, nc), path + [(nr, nc)]))

        return [], total_steps

    def _heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> int:
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
