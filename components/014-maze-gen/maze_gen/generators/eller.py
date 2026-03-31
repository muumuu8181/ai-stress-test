import random
from .base import MazeGenerator
from ..maze import Maze, CellType

class EllerGenerator(MazeGenerator):
    """
    Eller's algorithm.
    1. Grid dimensions must be odd.
    2. Fill the grid with walls.
    3. For each row:
       a. Assign set names to cells.
       b. Randomly connect adjacent cells that are in different sets.
       c. For each set, randomly connect at least one cell to the row below.
       d. Repeat for the next row.
       e. For the last row, connect all adjacent cells that are in different sets.
    """

    def generate(self, maze: Maze) -> None:
        # Initial grid with walls
        for r in range(maze.grid_height):
            for c in range(maze.grid_width):
                maze.set_cell(r, c, CellType.WALL)

        next_set_id = 0
        current_row_sets = [None] * maze.width

        for r in range(1, maze.grid_height - 1, 2):
            # Assign set names to cells
            for c in range(maze.width):
                if current_row_sets[c] is None:
                    current_row_sets[c] = next_set_id
                    next_set_id += 1
                maze.set_cell(r, 2 * c + 1, CellType.PATH)

            # Randomly connect adjacent cells
            for c in range(maze.width - 1):
                if current_row_sets[c] != current_row_sets[c + 1]:
                    if r == maze.grid_height - 2 or random.choice([True, False]):
                        # Merge sets and remove wall
                        old_set_id = current_row_sets[c + 1]
                        new_set_id = current_row_sets[c]
                        for i in range(maze.width):
                            if current_row_sets[i] == old_set_id:
                                current_row_sets[i] = new_set_id
                        maze.set_cell(r, 2 * (c + 1), CellType.PATH)

            # Randomly connect to the row below
            if r < maze.grid_height - 2:
                next_row_sets = [None] * maze.width
                sets_in_row = {}
                for c in range(maze.width):
                    set_id = current_row_sets[c]
                    if set_id not in sets_in_row:
                        sets_in_row[set_id] = []
                    sets_in_row[set_id].append(c)

                for set_id, columns in sets_in_row.items():
                    # Pick at least one column to connect down
                    num_to_connect = random.randint(1, len(columns))
                    random.shuffle(columns)
                    for i in range(num_to_connect):
                        c = columns[i]
                        maze.set_cell(r + 1, 2 * c + 1, CellType.PATH)
                        next_row_sets[c] = set_id

                current_row_sets = next_row_sets
