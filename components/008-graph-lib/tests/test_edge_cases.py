import pytest
from graph_algo.graph import DirectedGraph, UndirectedGraph
from graph_algo.search import bfs, dfs, has_cycle, find_connected_components
from graph_algo.topology import topological_sort
from graph_algo.shortest_path import dijkstra, bellman_ford
from graph_algo.mst import kruskal, prim


def test_empty_graph():
    g = DirectedGraph()
    assert bfs(g, 1) == []
    assert dfs(g, 1) == []
    assert not has_cycle(g)
    assert find_connected_components(g) == []
    assert topological_sort(g) == []


def test_single_node_graph():
    g = UndirectedGraph()
    g.add_vertex(1)
    assert bfs(g, 1) == [1]
    assert dfs(g, 1) == [1]
    assert not has_cycle(g)
    assert find_connected_components(g) == [{1}]

    g_dir = DirectedGraph()
    g_dir.add_vertex(1)
    assert topological_sort(g_dir) == [1]


def test_disconnected_graph_traversal():
    g = UndirectedGraph()
    g.add_edge(1, 2)
    g.add_vertex(3)
    assert bfs(g, 1) == [1, 2]
    assert bfs(g, 3) == [3]


def test_topo_sort_undirected_error():
    g = UndirectedGraph()
    g.add_edge(1, 2)
    with pytest.raises(ValueError, match="Topological sort is for directed graphs"):
        topological_sort(g)


def test_topo_sort_cycle_error():
    g = DirectedGraph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 1)
    with pytest.raises(ValueError, match="Graph contains a cycle"):
        topological_sort(g)


def test_dijkstra_no_path():
    g = DirectedGraph(weighted=True)
    g.add_vertex(1)
    g.add_vertex(2)
    distances, _ = dijkstra(g, 1)
    assert distances[2] == float("inf")


def test_bellman_ford_no_path():
    g = DirectedGraph(weighted=True)
    g.add_vertex(1)
    g.add_vertex(2)
    distances, _ = bellman_ford(g, 1)
    assert distances[2] == float("inf")


def test_heterogeneous_vertex_types():
    # Adjacency matrix sorting
    g = UndirectedGraph()
    g.add_edge(1, "A")
    g.add_edge("B", 2.5)
    nodes, matrix = g.get_adjacency_matrix()
    assert len(nodes) == 4

    # Dijkstra and tie-breaking
    g_dir = DirectedGraph(weighted=True)
    g_dir.add_edge("S", 1, weight=1)
    g_dir.add_edge("S", "A", weight=1)
    distances, _ = dijkstra(g_dir, "S")
    assert distances[1] == 1
    assert distances["A"] == 1

    # Kruskal de-duplication
    g_undir = UndirectedGraph(weighted=True)
    g_undir.add_edge(1, "A", 1)
    g_undir.add_edge("A", 1, 1)  # Duplicate edge
    mst = kruskal(g_undir)
    assert len(mst) == 1

    # Prim tie-breaking
    g_prim = UndirectedGraph(weighted=True)
    g_prim.add_edge("S", 1, 1)
    g_prim.add_edge("S", "A", 1)
    mst_prim = prim(g_prim)
    assert len(mst_prim) == 2

    # Connected components preservation of isolated vertices
    g_iso = DirectedGraph()
    g_iso.add_vertex(1)
    g_iso.add_vertex("A")
    g_iso.add_edge(1, 2)
    components = find_connected_components(g_iso)
    # Expected components: {1, 2} and {"A"}
    assert len(components) == 2
    comp_sets = [set(c) for c in components]
    assert {1, 2} in comp_sets
    assert {"A"} in comp_sets
