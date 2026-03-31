import pytest
from taskrunner.core import Task, TaskGraph

def test_topological_sort():
    t1 = Task("t1")
    t2 = Task("t2", dependencies=["t1"])
    t3 = Task("t3", dependencies=["t1", "t2"])

    graph = TaskGraph([t1, t2, t3])
    order = graph.get_execution_order()

    assert [t.name for t in order] == ["t1", "t2", "t3"]

def test_circular_dependency():
    t1 = Task("t1", dependencies=["t2"])
    t2 = Task("t2", dependencies=["t1"])

    graph = TaskGraph([t1, t2])
    with pytest.raises(ValueError, match="Circular dependency"):
        graph.get_execution_order()

def test_missing_dependency():
    t1 = Task("t1", dependencies=["t2"])

    graph = TaskGraph([t1])
    with pytest.raises(ValueError, match="Task 't2' not found"):
        graph.get_execution_order()

def test_target_subset():
    t1 = Task("t1")
    t2 = Task("t2", dependencies=["t1"])
    t3 = Task("t3")

    graph = TaskGraph([t1, t2, t3])
    order = graph.get_execution_order(["t2"])

    assert [t.name for t in order] == ["t1", "t2"]
