from typing import Any, List, Deque
from collections import deque
from .graph import Graph

def topological_sort(graph: Graph) -> List[Any]:
    """
    Performs a topological sort on a Directed Acyclic Graph (DAG).

    Args:
        graph: The directed graph.

    Returns:
        A list of nodes in topological order.

    Raises:
        ValueError: If the graph is undirected or contains a cycle.
    """
    if not graph.directed:
        raise ValueError("Topological sort is for directed graphs")

    in_degree = {u: 0 for u in graph.vertices}
    for u in graph.adj:
        for v in graph.adj[u]:
            in_degree[v] += 1

    queue: Deque[Any] = deque([u for u in graph.vertices if in_degree[u] == 0])
    result = []

    while queue:
        u = queue.popleft()
        result.append(u)

        for v in graph.get_neighbors(u):
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    if len(result) != len(graph.vertices):
        raise ValueError("Graph contains a cycle")

    return result
