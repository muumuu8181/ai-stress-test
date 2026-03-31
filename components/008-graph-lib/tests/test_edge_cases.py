import pytest
from graphlib.graph import DirectedGraph, UndirectedGraph
from graphlib.search import bfs, dfs, has_cycle, find_connected_components
from graphlib.topology import topological_sort
from graphlib.shortest_path import dijkstra, bellman_ford


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
