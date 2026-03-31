import pytest
from maze_gen.maze import Maze, CellType
from maze_gen.solvers.bfs import BFSSolver
from maze_gen.solvers.dfs import DFSSolver
from maze_gen.solvers.astar import AStarSolver
from maze_gen.solvers.wall_follower import WallFollowerSolver

@pytest.fixture
def simple_maze():
    """A 3x3 (cell) maze with a single path from (1,1) to (5,5)."""
    maze = Maze(3, 3)
    # (1,1) -> (1,2) -> (1,3) -> (2,3) -> (3,3) -> (4,3) -> (5,3) -> (5,4) -> (5,5)
    path = [(1, 1), (1, 2), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (5, 4), (5, 5)]
    for r, c in path:
        maze.set_cell(r, c, CellType.PATH)
    return maze

def test_bfs_shortest_path(simple_maze):
    solver = BFSSolver()
    path, steps = solver.solve(simple_maze)
    assert len(path) == 9
    assert path[-1] == (5, 5)

def test_dfs_path(simple_maze):
    solver = DFSSolver()
    path, steps = solver.solve(simple_maze)
    assert len(path) > 0
    assert path[-1] == (5, 5)

def test_astar_shortest_path(simple_maze):
    solver = AStarSolver()
    path, steps = solver.solve(simple_maze)
    assert len(path) == 9
    assert path[-1] == (5, 5)

def test_wall_follower_path(simple_maze):
    solver = WallFollowerSolver()
    path, steps = solver.solve(simple_maze)
    assert len(path) > 0
    assert path[-1] == (5, 5)

def test_unsolvable_maze():
    maze = Maze(3, 3)
    # All walls except start
    maze.set_cell(1, 1, CellType.PATH)
    # Goal is (5,5) and it's a wall by default

    solvers = [BFSSolver(), DFSSolver(), AStarSolver(), WallFollowerSolver()]
    for solver in solvers:
        path, steps = solver.solve(maze)
        assert path == []
