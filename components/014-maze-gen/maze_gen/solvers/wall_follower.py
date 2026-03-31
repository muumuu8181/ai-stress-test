from typing import List, Tuple
from .base import MazeSolver
from ..maze import Maze, CellType

class WallFollowerSolver(MazeSolver):
    """
    Wall-following algorithm (left-hand rule).
    Does not guarantee the shortest path and may get stuck in loops
    if the goal is not reachable along the wall.
    """

    def solve(self, maze: Maze) -> Tuple[List[Tuple[int, int]], int]:
        start = maze.start
        goal = maze.goal

        # directions: 0: right, 1: down, 2: left, 3: up
        # clockwise order
        drs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        current_dir = 1 # Start by facing down

        r, c = start
        path = [(r, c)]
        steps = 0
        visited_states = set()

        while (r, c) != goal:
            steps += 1
            # Add state (position and direction) to detect loops
            state = (r, c, current_dir)
            if state in visited_states:
                # Loop detected
                return [], steps
            visited_states.add(state)

            # Left-hand rule: try left, then forward, then right, then back
            # (current_dir - 1) % 4 is the direction to the left
            found_move = False
            for i in range(-1, 3):
                test_dir = (current_dir + i) % 4
                dr, dc = drs[test_dir]
                nr, nc = r + dr, c + dc

                if maze.is_within_bounds(nr, nc) and \
                   maze.get_cell(nr, nc) == CellType.PATH:
                    r, c = nr, nc
                    current_dir = test_dir
                    path.append((r, c))
                    found_move = True
                    break

            if not found_move:
                # Should not happen in a maze with surrounding walls,
                # but could happen if start is isolated
                return [], steps

        return path, steps
