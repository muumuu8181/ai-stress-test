# Maze Generator & Solver

A Python-based maze generator and solver using only the standard library.

## Features

### Generation Algorithms
- **Boutaoshi (Stick-down) method**: A simple algorithm that places sticks and knocks them down.
- **Anahori (Digging) method**: A recursive digging algorithm.
- **Randomized Kruskal's algorithm**: Creates a spanning tree by randomly removing walls.
- **Randomized Prim's algorithm**: Grows a maze from a starting point.
- **Eller's algorithm**: Generates a maze row-by-row, efficient for large mazes.

### Solvers
- **BFS (Breadth-First Search)**: Guarantees the shortest path.
- **DFS (Depth-First Search)**: Explores as far as possible before backtracking.
- **A\* Search**: Uses Manhattan distance heuristic for efficient pathfinding.
- **Wall Follower (Left-hand rule)**: Follows the left wall to find the exit.

### IO & Serialization
- **ASCII Visualization**: Display the maze in the terminal.
- **PBM Image Export**: Export the maze as a black-and-white image.
- **JSON Serialization**: Save and load mazes as JSON.

## Usage

```python
from maze_gen.maze import Maze
from maze_gen.generators.kruskal import KruskalGenerator
from maze_gen.solvers.astar import AStarSolver
from maze_gen.io import to_ascii

# 1. Create a maze (width x height)
width, height = 15, 10
maze = Maze(width, height)

# 2. Generate a maze using Kruskal's algorithm
generator = KruskalGenerator()
generator.generate(maze)

# 3. Solve the maze using A*
solver = AStarSolver()
path, steps = solver.solve(maze)

# 4. Display the result
print(f"Solved in {steps} steps.")
print(to_ascii(maze, path=path))
```

## Running Tests

To run the tests and check coverage:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/components/014-maze-gen
pytest components/014-maze-gen/tests/ --cov=components/014-maze-gen/maze_gen
```

## Requirements
- Python 3.7+
- (Optional) `pytest`, `pytest-cov` for testing
