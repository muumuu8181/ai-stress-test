import pytest
from graph_algo.graph import Graph, DirectedGraph, UndirectedGraph


def test_graph_add_vertex():
    g = Graph()
    g.add_vertex(1)
    assert 1 in g.vertices
    assert g.adj[1] == {}


def test_graph_add_edge_undirected():
    g = UndirectedGraph()
    g.add_edge(1, 2)
    assert 1 in g.vertices
    assert 2 in g.vertices
    assert g.adj[1][2] == 1
    assert g.adj[2][1] == 1


def test_graph_add_edge_directed():
    g = DirectedGraph()
    g.add_edge(1, 2)
    assert 1 in g.vertices
    assert 2 in g.vertices
    assert g.adj[1][2] == 1
    assert 1 not in g.adj[2]


def test_graph_weighted_edge():
    g = UndirectedGraph(weighted=True)
    g.add_edge(1, 2, 5)
    assert g.adj[1][2] == 5
    assert g.adj[2][1] == 5


def test_graph_unweighted_edge_ignores_weight():
    g = UndirectedGraph(weighted=False)
    g.add_edge(1, 2, 5)
    assert g.adj[1][2] == 1
    assert g.adj[2][1] == 1


def test_graph_remove_edge():
    g = UndirectedGraph()
    g.add_edge(1, 2)
    g.remove_edge(1, 2)
    assert 2 not in g.adj[1]
    assert 1 not in g.adj[2]


def test_get_neighbors():
    g = DirectedGraph()
    g.add_edge(1, 2)
    g.add_edge(1, 3)
    neighbors = g.get_neighbors(1)
    assert neighbors == {2: 1, 3: 1}


def test_get_adjacency_matrix():
    g = UndirectedGraph()
    g.add_edge(1, 2)
    nodes, matrix = g.get_adjacency_matrix()
    assert nodes == [1, 2]
    assert matrix == [[0, 1], [1, 0]]


def test_get_adjacency_matrix_weighted():
    g = UndirectedGraph(weighted=True)
    g.add_edge("A", "B", 3)
    nodes, matrix = g.get_adjacency_matrix()
    assert nodes == ["A", "B"]
    assert matrix == [[0, 3], [3, 0]]
