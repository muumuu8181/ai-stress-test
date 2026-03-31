import pytest
from graphlib.graph import UndirectedGraph
from graphlib.mst import kruskal, prim


def test_kruskal():
    g = UndirectedGraph(weighted=True)
    g.add_edge("A", "B", 1)
    g.add_edge("B", "C", 3)
    g.add_edge("A", "C", 3)
    g.add_edge("C", "D", 1)
    g.add_edge("B", "D", 4)

    mst = kruskal(g)
    # Expected edges (in any order): (A,B,1), (C,D,1), (B,C,3)
    assert len(mst) == 3
    total_weight = sum(e[2] for e in mst)
    assert total_weight == 5


def test_prim():
    g = UndirectedGraph(weighted=True)
    g.add_edge("A", "B", 1)
    g.add_edge("B", "C", 3)
    g.add_edge("A", "C", 3)
    g.add_edge("C", "D", 1)
    g.add_edge("B", "D", 4)

    mst = prim(g)
    assert len(mst) == 3
    total_weight = sum(e[2] for e in mst)
    assert total_weight == 5


def test_mst_single_node():
    g = UndirectedGraph()
    g.add_vertex(1)
    assert kruskal(g) == []
    assert prim(g) == []


def test_mst_disconnected():
    g = UndirectedGraph(weighted=True)
    g.add_edge(1, 2, 1)
    g.add_edge(3, 4, 1)
    mst = kruskal(g)
    assert len(mst) == 2
    mst_prim = prim(g)
    # Prim's algorithm as implemented only finds MST for one component
    assert len(mst_prim) == 1
