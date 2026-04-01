import pytest
from unittest.mock import MagicMock
from profiler.core import Profiler
from profiler.models import FunctionStats

def test_internal_methods_coverage():
    p = Profiler(track_memory=True)

    # Mock a frame
    mock_code = MagicMock()
    mock_code.co_filename = "test.py"
    mock_code.co_firstlineno = 10
    mock_code.co_name = "mock_func"

    mock_frame = MagicMock()
    mock_frame.f_code = mock_code

    # Call internal methods
    p._handle_call(mock_frame)
    assert len(p.call_stack) == 1
    assert p.call_stack[0].stats.name == "mock_func"

    p._handle_return(mock_frame)
    assert len(p.call_stack) == 0
    assert "test.py:10(mock_func)" in p.function_stats

    # Call profile handler
    p._profile_handler(mock_frame, "call", None)
    p._profile_handler(mock_frame, "return", None)
    p._profile_handler(mock_frame, "c_call", None) # Should be ignored

def test_formatter_edge_cases():
    from profiler.formatter import StatsFormatter
    from profiler.models import ProfilerResult

    stats = {
        "test": FunctionStats(name="test", file_name="test.py", line_number=1, call_count=1, total_time=1.0, self_time=0.5, memory_usage=100)
    }
    result = ProfilerResult(function_stats=stats, call_graph=[])

    # Sort by different keys
    for key in ["self_time", "call_count", "memory_usage", "name"]:
        StatsFormatter.to_table(result, sort_by=key)

    # Filter with no match
    filtered = StatsFormatter.filter_stats(stats, pattern="nomatch")
    assert len(filtered) == 0

def test_models_repr():
    # To cover __post_init__ if it was missed
    fs = FunctionStats(name="f", file_name="m.py", line_number=1)
    assert fs.full_name == "m.py:1(f)"
