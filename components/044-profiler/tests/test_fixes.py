import sys
import tracemalloc
from profiler import Profiler, StatsFormatter, Profile

def test_hook_restoration():
    def dummy_hook(frame, event, arg):
        pass

    sys.setprofile(dummy_hook)
    try:
        p = Profiler()
        p.start()
        assert sys.getprofile() is not dummy_hook
        p.stop()
        assert sys.getprofile() is dummy_hook
    finally:
        sys.setprofile(None)

def test_tracemalloc_management():
    # Test if we don't stop it if we didn't start it
    tracemalloc.start()
    try:
        p = Profiler(track_memory=True)
        p.start()
        assert not p._started_tracemalloc
        p.stop()
        assert tracemalloc.is_tracing()
    finally:
        tracemalloc.stop()

    # Test if we do stop it if we did start it
    assert not tracemalloc.is_tracing()
    p = Profiler(track_memory=True)
    p.start()
    assert p._started_tracemalloc
    p.stop()
    assert not tracemalloc.is_tracing()

def test_flamegraph_uniqueness_and_no_double_count():
    from profiler.models import ProfilerResult, FunctionStats

    # Mocking call graph
    # Root (total 100) -> Child1 (total 40)
    #                  -> Child2 (total 30)
    # Self of Root should be 30.

    node_child1 = {
        "name": "child1",
        "full_name": "mod.py:10(child1)",
        "duration": 0.4,
        "children": []
    }
    node_child2 = {
        "name": "child2",
        "full_name": "mod.py:20(child2)",
        "duration": 0.3,
        "children": []
    }
    node_root = {
        "name": "root",
        "full_name": "mod.py:1(root)",
        "duration": 1.0,
        "children": [node_child1, node_child2]
    }

    result = ProfilerResult(function_stats={}, call_graph=[node_root])
    flame = StatsFormatter.to_flamegraph(result)

    lines = flame.splitlines()
    assert len(lines) == 3

    # Root self-time: 1.0 - 0.4 - 0.3 = 0.3 -> 300,000 us
    assert "mod.py:1(root) 300000" in lines
    # Child1 self-time: 0.4 -> 400,000 us
    assert "mod.py:1(root);mod.py:10(child1) 400000" in lines
    # Child2 self-time: 0.3 -> 300,000 us
    assert "mod.py:1(root);mod.py:20(child2) 300000" in lines

def test_no_internal_pollution():
    p = Profiler()
    def nested_func():
        pass

    with p:
        nested_func()

    results = p._results
    for key in results.function_stats:
        # Internal methods stop and __exit__ should be filtered out
        assert "stop" not in key
        assert "__exit__" not in key

def test_nested_decorator():
    import io
    from contextlib import redirect_stderr

    @Profile
    def inner():
        return "inner"

    @Profile
    def outer():
        return inner()

    f = io.StringIO()
    with redirect_stderr(f):
        result = outer()

    assert result == "inner"
    output = f.getvalue()
    # Should only have one set of profiling results (from the outer one)
    # because the inner one should detect the active profiler and skip.
    assert output.count("Profiling results for outer") == 1
    assert output.count("Profiling results for inner") == 0
