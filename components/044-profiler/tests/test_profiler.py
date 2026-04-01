import pytest
import time
import re
import json
from profiler import Profiler, Profile, StatsFormatter

def test_basic_profiling():
    p = Profiler()

    def func_a():
        time.sleep(0.01)
        func_b()

    def func_b():
        time.sleep(0.02)

    with p:
        func_a()

    results = p._results

    stats_keys = results.function_stats.keys()
    assert any("func_a" in k for k in stats_keys)
    assert any("func_b" in k for k in stats_keys)

    func_a_key = [k for k in stats_keys if "func_a" in k][0]
    func_b_key = [k for k in stats_keys if "func_b" in k][0]

    assert results.function_stats[func_a_key].call_count == 1
    assert results.function_stats[func_b_key].call_count == 1

    assert results.function_stats[func_a_key].total_time >= 0.03
    assert results.function_stats[func_b_key].total_time >= 0.02
    assert results.function_stats[func_a_key].self_time < 0.02

def test_manual_start_stop():
    p = Profiler()
    p.start()
    time.sleep(0.01)
    p.stop()
    # Should have caught 'sleep' if sys.setprofile handles built-ins?
    # Usually it doesn't unless it's a c_call.

def test_decorator_profiling():
    @Profile
    def decorated_func():
        return 42

    result = decorated_func()
    assert result == 42

def test_nested_calls():
    p = Profiler()

    def fib(n):
        if n <= 1: return n
        return fib(n-1) + fib(n-2)

    with p:
        fib(5)

    results = p._results
    fib_key = [k for k in results.function_stats.keys() if "fib" in k][0]
    assert results.function_stats[fib_key].call_count > 1

def test_memory_tracking():
    p = Profiler(track_memory=True)

    def alloc_mem():
        x = [0] * 1000000
        return x

    with p:
        alloc_mem()

    results = p._results
    alloc_key = [k for k in results.function_stats.keys() if "alloc_mem" in k][0]
    assert results.function_stats[alloc_key].memory_usage > 0

def test_filtering_and_sorting():
    p = Profiler()

    def apple(): pass
    def banana(): pass

    with p:
        apple()
        banana()
        banana()

    results = p._results

    # Filtering
    filtered = StatsFormatter.filter_stats(results.function_stats, pattern="apple")
    assert len(filtered) == 1
    assert filtered[0].name == "apple"

    # Sorting
    sorted_stats = StatsFormatter.sort_stats(list(results.function_stats.values()), sort_by="call_count")
    assert sorted_stats[0].name == "banana"

    # Invalid sort key defaults to total_time
    sorted_stats2 = StatsFormatter.sort_stats(list(results.function_stats.values()), sort_by="invalid")
    assert len(sorted_stats2) == len(results.function_stats)

def test_output_formats():
    p = Profiler()
    def my_func(): pass
    with p:
        my_func()

    results = p._results

    table = StatsFormatter.to_table(results)
    assert "my_func" in table

    # Test long name truncation in table
    long_name_key = "a" * 100
    results.function_stats[long_name_key] = results.function_stats[list(results.function_stats.keys())[0]]
    results.function_stats[long_name_key].full_name = long_name_key
    table_long = StatsFormatter.to_table(results)
    assert "..." in table_long

    js = StatsFormatter.to_json(results)
    data = json.loads(js)
    assert "functions" in data

    flame = StatsFormatter.to_flamegraph(results)
    assert "my_func" in flame

def test_exception_handling():
    p = Profiler()

    def buggy_func():
        raise ValueError("Oops")

    try:
        with p:
            buggy_func()
    except ValueError:
        pass

    results = p._results
    assert any("buggy_func" in k for k in results.function_stats.keys())

def test_empty_profiling():
    p = Profiler()
    with p:
        pass
    results = p._results
    for key in results.function_stats:
        assert "__exit__" in key or "stop" in key

def test_profiler_idempotent_start():
    p = Profiler()
    p.start()
    p.start() # Should return immediately
    p.stop()
    assert not p._is_profiling

def test_profile_method():
    p = Profiler()
    with p.profile():
        pass
    assert p._results is not None
