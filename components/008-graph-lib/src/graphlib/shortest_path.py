import heapq
from typing import Any, Dict, List, Optional, Union, Tuple
from .graph import Graph

def dijkstra(graph: Graph, start_node: Any) -> Tuple[Dict[Any, Union[int, float]], Dict[Any, Optional[Any]]]:
    """
    Computes the shortest paths from a start node to all other reachable nodes
    using Dijkstra's algorithm.

    Args:
        graph: The graph (must have non-negative edge weights).
        start_node: The node to start the calculation from.

    Returns:
        A tuple of (distances, predecessors):
        - distances: A dictionary mapping nodes to their shortest distance from start_node.
        - predecessors: A dictionary mapping nodes to their predecessor in the shortest path.
    """
    if start_node not in graph.vertices:
        return {}, {}

    distances: Dict[Any, Union[int, float]] = {node: float('inf') for node in graph.vertices}
    predecessors: Dict[Any, Optional[Any]] = {node: None for node in graph.vertices}
    distances[start_node] = 0

    pq = [(0, start_node)]

    while pq:
        current_distance, u = heapq.heappop(pq)

        if current_distance > distances[u]:
            continue

        for v, weight in graph.get_neighbors(u).items():
            distance = current_distance + weight

            if distance < distances[v]:
                distances[v] = distance
                predecessors[v] = u
                heapq.heappush(pq, (distance, v))

    return distances, predecessors

def bellman_ford(graph: Graph, start_node: Any) -> Tuple[Dict[Any, Union[int, float]], Dict[Any, Optional[Any]]]:
    """
    Computes the shortest paths from a start node to all other reachable nodes
    using the Bellman-Ford algorithm.
    Handles negative edge weights and detects negative cycles.

    Args:
        graph: The graph.
        start_node: The node to start the calculation from.

    Returns:
        A tuple of (distances, predecessors):
        - distances: A dictionary mapping nodes to their shortest distance from start_node.
        - predecessors: A dictionary mapping nodes to their predecessor in the shortest path.

    Raises:
        ValueError: If a negative weight cycle is detected.
    """
    if start_node not in graph.vertices:
        return {}, {}

    distances: Dict[Any, Union[int, float]] = {node: float('inf') for node in graph.vertices}
    predecessors: Dict[Any, Optional[Any]] = {node: None for node in graph.vertices}
    distances[start_node] = 0

    vertices = list(graph.vertices)
    for _ in range(len(vertices) - 1):
        for u in vertices:
            for v, weight in graph.get_neighbors(u).items():
                if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    predecessors[v] = u

    for u in vertices:
        for v, weight in graph.get_neighbors(u).items():
            if distances[u] != float('inf') and distances[u] + weight < distances[v]:
                raise ValueError("Graph contains a negative weight cycle")

    return distances, predecessors
