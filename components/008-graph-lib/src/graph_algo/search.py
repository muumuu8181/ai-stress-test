from typing import Any, List, Set, Deque, Callable, Optional
from collections import deque
from .graph import Graph


def bfs(
    graph: Graph, start_node: Any, visitor: Optional[Callable[[Any], None]] = None
) -> List[Any]:
    """
    Performs a Breadth-First Search on the graph starting from start_node.

    Args:
        graph: The graph to traverse.
        start_node: The node to start the traversal from.
        visitor: Optional callback function called for each visited node.

    Returns:
        A list of nodes in the order they were visited.
    """
    if start_node not in graph.vertices:
        return []

    visited: Set[Any] = {start_node}
    queue: Deque[Any] = deque([start_node])
    order: List[Any] = []

    while queue:
        u = queue.popleft()
        order.append(u)
        if visitor:
            visitor(u)

        for v in graph.get_neighbors(u):
            if v not in visited:
                visited.add(v)
                queue.append(v)

    return order


def dfs(
    graph: Graph, start_node: Any, visitor: Optional[Callable[[Any], None]] = None
) -> List[Any]:
    """
    Performs a Depth-First Search on the graph starting from start_node.

    Args:
        graph: The graph to traverse.
        start_node: The node to start the traversal from.
        visitor: Optional callback function called for each visited node.

    Returns:
        A list of nodes in the order they were visited.
    """
    if start_node not in graph.vertices:
        return []

    visited: Set[Any] = set()
    order: List[Any] = []

    def _dfs_recursive(u: Any):
        visited.add(u)
        order.append(u)
        if visitor:
            visitor(u)

        for v in graph.get_neighbors(u):
            if v not in visited:
                _dfs_recursive(v)

    _dfs_recursive(start_node)
    return order


def find_connected_components(graph: Graph) -> List[Set[Any]]:
    """
    Finds all connected components in an undirected graph.
    For directed graphs, this function finds weakly connected components by
    treating the edges as undirected.

    Args:
        graph: The graph.

    Returns:
        A list of sets, where each set contains vertices of a connected component.
    """
    if graph.directed:
        # Create an undirected version to find weakly connected components
        undirected_graph = Graph(directed=False, weighted=graph.weighted)
        for v in graph.vertices:
            undirected_graph.add_vertex(v)
        for u in graph.adj:
            for v, weight in graph.adj[u].items():
                undirected_graph.add_edge(u, v, weight)
        return find_connected_components(undirected_graph)

    visited: Set[Any] = set()
    components: List[Set[Any]] = []

    for v in graph.vertices:
        if v not in visited:
            component = set(bfs(graph, v))
            components.append(component)
            visited.update(component)

    return components


def has_cycle(graph: Graph) -> bool:
    """
    Detects if the graph contains a cycle.

    Args:
        graph: The graph.

    Returns:
        True if the graph contains at least one cycle, False otherwise.
    """
    if graph.directed:
        return _has_cycle_directed(graph)
    else:
        return _has_cycle_undirected(graph)


def _has_cycle_directed(graph: Graph) -> bool:
    visited: Set[Any] = set()
    rec_stack: Set[Any] = set()

    def _dfs_cycle(u: Any) -> bool:
        visited.add(u)
        rec_stack.add(u)

        for v in graph.get_neighbors(u):
            if v not in visited:
                if _dfs_cycle(v):
                    return True
            elif v in rec_stack:
                return True

        rec_stack.remove(u)
        return False

    for node in graph.vertices:
        if node not in visited:
            if _dfs_cycle(node):
                return True
    return False


def _has_cycle_undirected(graph: Graph) -> bool:
    visited: Set[Any] = set()

    def _dfs_cycle(u: Any, parent: Any) -> bool:
        visited.add(u)

        for v in graph.get_neighbors(u):
            if v not in visited:
                if _dfs_cycle(v, u):
                    return True
            elif v != parent:
                return True
        return False

    for node in graph.vertices:
        if node not in visited:
            if _dfs_cycle(node, None):
                return True
    return False
