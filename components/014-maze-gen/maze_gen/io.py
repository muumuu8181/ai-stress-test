from .maze import Maze, CellType
from typing import List, Tuple

def to_ascii(maze: Maze, path: List[Tuple[int, int]] = None) -> str:
    """
    Represent the maze as ASCII.
    # : Wall
    . : Path
    S : Start
    G : Goal
    * : Path step (if path is provided)
    """
    path_set = set(path) if path else set()
    lines = []
    for r in range(maze.grid_height):
        row = []
        for c in range(maze.grid_width):
            if (r, c) == maze.start:
                row.append('S')
            elif (r, c) == maze.goal:
                row.append('G')
            elif (r, c) in path_set:
                row.append('*')
            elif maze.get_cell(r, c) == CellType.WALL:
                row.append('#')
            else:
                row.append(' ')
        lines.append("".join(row))
    return "\n".join(lines)

def to_pbm(maze: Maze, filepath: str) -> None:
    """
    Save the maze as a PBM (Portable BitMap) file.
    0: White (path)
    1: Black (wall)
    """
    with open(filepath, 'w') as f:
        f.write("P1\n")
        f.write(f"{maze.grid_width} {maze.grid_height}\n")
        for r in range(maze.grid_height):
            line = " ".join(str(int(maze.get_cell(r, c))) for c in range(maze.grid_width))
            f.write(line + "\n")
