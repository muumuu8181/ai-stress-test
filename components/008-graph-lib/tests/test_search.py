import pytest
from graph_algo.graph import UndirectedGraph, DirectedGraph
from graph_algo.search import bfs, dfs, find_connected_components, has_cycle


def test_bfs():
    g = UndirectedGraph()
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.add_edge(2, 4)
    g.add_edge(3, 4)
    order = bfs(g, 1)
    assert order[0] == 1
    assert set(order[1:3]) == {2, 3}
    assert order[3] == 4


def test_dfs():
    g = DirectedGraph()
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.add_edge(2, 4)
    order = dfs(g, 1)
    assert order[0] == 1
    # DFS order can vary depending on implementation detail (dictionary order)
    # but 2 must come before 4.
    idx2 = order.index(2)
    idx4 = order.index(4)
    assert idx2 < idx4


def test_connected_components():
    g = UndirectedGraph()
    g.add_edge(1, 2)
    g.add_edge(3, 4)
    g.add_vertex(5)
    components = find_connected_components(g)
    assert len(components) == 3
    # Convert each component to sorted list for comparison
    comp_sets = [set(c) for c in components]
    assert {1, 2} in comp_sets
    assert {3, 4} in comp_sets
    assert {5} in comp_sets


def test_has_cycle_undirected():
    g = UndirectedGraph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    assert not has_cycle(g)
    g.add_edge(3, 1)
    assert has_cycle(g)


def test_has_cycle_directed():
    g = DirectedGraph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    assert not has_cycle(g)
    g.add_edge(3, 1)
    assert has_cycle(g)


def test_has_cycle_directed_no_cycle_back_edge():
    g = DirectedGraph()
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.add_edge(2, 4)
    g.add_edge(3, 4)
    assert not has_cycle(g)
