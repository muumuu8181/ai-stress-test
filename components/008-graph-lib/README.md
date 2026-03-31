# Graph Algorithm Library

A Python library for graph algorithms using only the standard library.

## Features

- **Graph Construction**: Directed/Undirected, Weighted/Unweighted edges.
- **Search**: BFS, DFS, Cycle Detection, Connected Components.
- **Shortest Path**: Dijkstra's algorithm, Bellman-Ford algorithm.
- **Minimum Spanning Tree**: Kruskal's algorithm, Prim's algorithm.
- **Topological Sort**: Kahn's algorithm.
- **Representations**: Support for both Adjacency List and Adjacency Matrix.

## Installation

Add the `src` directory to your `PYTHONPATH`.

## Usage Examples

### 1. Creating a Graph

```python
from graphlib import DirectedGraph, UndirectedGraph

# Directed Weighted Graph
g = DirectedGraph(weighted=True)
g.add_edge('A', 'B', 5)
g.add_edge('B', 'C', 3)

# Adjacency Matrix
nodes, matrix = g.get_adjacency_matrix()
print(nodes)   # ['A', 'B', 'C']
print(matrix)  # [[0, 5, None], [None, 0, 3], [None, None, 0]]
```

### 2. Search Algorithms

```python
from graphlib import bfs, dfs, has_cycle

g = UndirectedGraph()
g.add_edge(1, 2)
g.add_edge(2, 3)

print(bfs(g, 1))      # [1, 2, 3]
print(has_cycle(g))   # False
```

### 3. Shortest Path

```python
from graphlib import dijkstra, bellman_ford

g = DirectedGraph(weighted=True)
g.add_edge('A', 'B', 1)
g.add_edge('B', 'C', 2)
g.add_edge('A', 'C', 4)

distances, predecessors = dijkstra(g, 'A')
print(distances['C'])  # 3
```

### 4. Minimum Spanning Tree (MST)

```python
from graphlib import UndirectedGraph, kruskal, prim

g = UndirectedGraph(weighted=True)
g.add_edge('A', 'B', 1)
g.add_edge('B', 'C', 3)
g.add_edge('A', 'C', 2)

mst = kruskal(g)
print(mst)  # [('A', 'B', 1), ('A', 'C', 2)]
```

### 5. Topological Sort

```python
from graphlib import DirectedGraph, topological_sort

g = DirectedGraph()
g.add_edge('A', 'B')
g.add_edge('B', 'C')

print(topological_sort(g))  # ['A', 'B', 'C']
```

## Running Tests

```bash
pytest tests/
```
