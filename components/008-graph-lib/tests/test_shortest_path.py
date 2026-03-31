import pytest
from graphlib.graph import DirectedGraph, UndirectedGraph
from graphlib.shortest_path import dijkstra, bellman_ford


def test_dijkstra():
    g = DirectedGraph(weighted=True)
    g.add_edge(1, 2, 1)
    g.add_edge(1, 3, 4)
    g.add_edge(2, 3, 2)
    g.add_edge(2, 4, 6)
    g.add_edge(3, 4, 3)

    distances, predecessors = dijkstra(g, 1)
    assert distances[1] == 0
    assert distances[2] == 1
    assert distances[3] == 3
    assert distances[4] == 6
    assert predecessors[4] == 3


def test_bellman_ford():
    g = DirectedGraph(weighted=True)
    g.add_edge(1, 2, 1)
    g.add_edge(1, 3, 4)
    g.add_edge(2, 3, 2)
    g.add_edge(2, 4, 6)
    g.add_edge(3, 4, 3)

    distances, predecessors = bellman_ford(g, 1)
    assert distances[4] == 6


def test_bellman_ford_negative_weights():
    g = DirectedGraph(weighted=True)
    g.add_edge(1, 2, 10)
    g.add_edge(2, 3, -5)
    g.add_edge(1, 3, 7)

    distances, _ = bellman_ford(g, 1)
    assert distances[3] == 5


def test_bellman_ford_negative_cycle():
    g = DirectedGraph(weighted=True)
    g.add_edge(1, 2, 1)
    g.add_edge(2, 3, -5)
    g.add_edge(3, 1, 1)

    with pytest.raises(ValueError, match="Graph contains a negative weight cycle"):
        bellman_ford(g, 1)
