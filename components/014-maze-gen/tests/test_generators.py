import pytest
from maze_gen.maze import Maze, CellType
from maze_gen.generators.boutaoshi import BoutaoshiGenerator
from maze_gen.generators.anahori import AnahoriGenerator
from maze_gen.generators.kruskal import KruskalGenerator
from maze_gen.generators.prim import PrimGenerator
from maze_gen.generators.eller import EllerGenerator
from maze_gen.solvers.bfs import BFSSolver

@pytest.mark.parametrize("generator_class", [
    BoutaoshiGenerator,
    AnahoriGenerator,
    KruskalGenerator,
    PrimGenerator,
    EllerGenerator
])
def test_generators_solvable(generator_class):
    width, height = 11, 11
    maze = Maze(width, height)
    generator = generator_class()
    generator.generate(maze)

    # Check if solvable
    solver = BFSSolver()
    path, steps = solver.solve(maze)
    assert len(path) > 0
    assert path[0] == maze.start
    assert path[-1] == maze.goal

def test_maze_invalid_size():
    with pytest.raises(ValueError):
        Maze(0, 5)
    with pytest.raises(ValueError):
        Maze(5, -1)

def test_maze_bounds():
    maze = Maze(5, 5)
    assert maze.is_within_bounds(0, 0)
    assert maze.is_within_bounds(10, 10)
    assert not maze.is_within_bounds(-1, 0)
    assert not maze.is_within_bounds(0, 11)

def test_maze_set_start_goal_out_of_bounds():
    maze = Maze(5, 5)
    with pytest.raises(ValueError):
        maze.set_start(-1, 0)
    with pytest.raises(ValueError):
        maze.set_goal(0, 11)
