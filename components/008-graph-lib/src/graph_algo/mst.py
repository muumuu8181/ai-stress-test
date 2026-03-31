import heapq
import itertools
from typing import Any, List, Tuple, Dict, Union
from .graph import Graph


class UnionFind:
    def __init__(self, elements: List[Any]):
        self.parent = {el: el for el in elements}
        self.rank = {el: 0 for el in elements}

    def find(self, i: Any) -> Any:
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i: Any, j: Any) -> None:
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            if self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            elif self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_i] = root_j
                self.rank[root_j] += 1


def kruskal(graph: Graph) -> List[Tuple[Any, Any, Union[int, float]]]:
    """
    Finds the Minimum Spanning Tree of an undirected graph using Kruskal's algorithm.

    Args:
        graph: The undirected graph.

    Returns:
        A list of edges (u, v, weight) that form the MST.
    """
    if graph.directed:
        raise ValueError("Kruskal's algorithm is for undirected graphs")

    edges = []
    seen_edges = set()
    for u in graph.adj:
        for v, weight in graph.adj[u].items():
            # Use a canonical order to avoid duplicates in undirected graph
            # sorted((u, v)) might fail with heterogeneous types, so use a more robust key
            u_key = (str(type(u)), str(u))
            v_key = (str(type(v)), str(v))
            if u_key < v_key:
                canonical_edge = (u, v, weight)
            else:
                canonical_edge = (v, u, weight)

            if canonical_edge not in seen_edges:
                edges.append((u, v, weight))
                seen_edges.add(canonical_edge)

    edges.sort(key=lambda x: x[2])

    uf = UnionFind(list(graph.vertices))
    mst = []

    for u, v, weight in edges:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            mst.append((u, v, weight))

    return mst


def prim(graph: Graph) -> List[Tuple[Any, Any, Union[int, float]]]:
    """
    Finds the Minimum Spanning Tree of an undirected graph using Prim's algorithm.

    Args:
        graph: The undirected graph.

    Returns:
        A list of edges (u, v, weight) that form the MST.
    """
    if graph.directed:
        raise ValueError("Prim's algorithm is for undirected graphs")

    if not graph.vertices:
        return []

    start_node = next(iter(graph.vertices))
    visited = {start_node}
    edges = []
    mst = []
    counter = itertools.count()

    # (weight, counter, u, v)
    for v, weight in graph.get_neighbors(start_node).items():
        heapq.heappush(edges, (weight, next(counter), start_node, v))

    while edges:
        weight, _, u, v = heapq.heappop(edges)
        if v not in visited:
            visited.add(v)
            mst.append((u, v, weight))

            for next_v, next_weight in graph.get_neighbors(v).items():
                if next_v not in visited:
                    heapq.heappush(edges, (next_weight, next(counter), v, next_v))

    return mst
