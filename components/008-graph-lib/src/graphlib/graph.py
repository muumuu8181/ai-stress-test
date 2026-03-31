from typing import Dict, List, Set, Tuple, Optional, Any, Union


class Graph:
    """
    A base class representing a graph.
    Supports both directed/undirected and weighted/unweighted edges.
    Internal representation uses an adjacency list.
    """

    def __init__(self, directed: bool = False, weighted: bool = False) -> None:
        """
        Initializes a graph.

        Args:
            directed: Whether the graph is directed.
            weighted: Whether the graph is weighted.
        """
        self.directed = directed
        self.weighted = weighted
        self.vertices: Set[Any] = set()
        self.adj: Dict[Any, Dict[Any, Union[int, float]]] = {}

    def add_vertex(self, v: Any) -> None:
        """
        Adds a vertex to the graph.

        Args:
            v: The vertex to add.
        """
        if v not in self.vertices:
            self.vertices.add(v)
            self.adj[v] = {}

    def add_edge(self, u: Any, v: Any, weight: Union[int, float] = 1) -> None:
        """
        Adds an edge to the graph.

        Args:
            u: Starting vertex.
            v: Ending vertex.
            weight: Edge weight (default is 1).
        """
        self.add_vertex(u)
        self.add_vertex(v)

        actual_weight = weight if self.weighted else 1
        self.adj[u][v] = actual_weight

        if not self.directed:
            self.adj[v][u] = actual_weight

    def remove_edge(self, u: Any, v: Any) -> None:
        """
        Removes an edge from the graph.

        Args:
            u: Starting vertex.
            v: Ending vertex.
        """
        if u in self.adj and v in self.adj[u]:
            del self.adj[u][v]
        if not self.directed:
            if v in self.adj and u in self.adj[v]:
                del self.adj[v][u]

    def get_neighbors(self, v: Any) -> Dict[Any, Union[int, float]]:
        """
        Returns the neighbors of a vertex and their edge weights.

        Args:
            v: The vertex.

        Returns:
            A dictionary of neighbors and weights.
        """
        return self.adj.get(v, {})

    def get_adjacency_list(self) -> Dict[Any, Dict[Any, Union[int, float]]]:
        """
        Returns the adjacency list representation of the graph.

        Returns:
            A dictionary where keys are vertices and values are dictionaries of neighbors and weights.
        """
        return self.adj

    def get_adjacency_matrix(
        self,
    ) -> Tuple[List[Any], List[List[Optional[Union[int, float]]]]]:
        """
        Returns the adjacency matrix representation of the graph.

        Returns:
            A tuple containing:
            - A list of vertices (in order of matrix rows/columns).
            - The adjacency matrix as a list of lists.
        """
        nodes = sorted(list(self.vertices))
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        size = len(nodes)

        # Initialize matrix with None (representing no edge)
        # Note: Depending on requirements, 0 or infinity might be used.
        # Here we use None for "no edge", but diagonal is 0.
        matrix: List[List[Optional[Union[int, float]]]] = [
            [None for _ in range(size)] for _ in range(size)
        ]

        for i in range(size):
            matrix[i][i] = 0

        for u in self.adj:
            for v, weight in self.adj[u].items():
                matrix[node_to_idx[u]][node_to_idx[v]] = weight

        return nodes, matrix

    def __str__(self) -> str:
        return f"Graph(directed={self.directed}, weighted={self.weighted}, vertices={self.vertices}, adj={self.adj})"


class DirectedGraph(Graph):
    """
    Represents a directed graph.
    """

    def __init__(self, weighted: bool = False) -> None:
        super().__init__(directed=True, weighted=weighted)


class UndirectedGraph(Graph):
    """
    Represents an undirected graph.
    """

    def __init__(self, weighted: bool = False) -> None:
        super().__init__(directed=False, weighted=weighted)
