import sys
import time
import tracemalloc
import functools
import re
from typing import Dict, List, Optional, Any, Callable, Type
from types import FrameType, TracebackType

from .models import FunctionStats, CallFrame, ProfilerResult


class Profiler:
    """Core profiling engine for function-level execution and memory tracking."""

    def __init__(self, track_memory: bool = False):
        self.track_memory = track_memory
        self.function_stats: Dict[str, FunctionStats] = {}
        self.call_stack: List[CallFrame] = []
        self._is_profiling = False
        self._results: Optional[ProfilerResult] = None
        self._root_frames: List[Dict] = []
        self._current_tree_path: List[Dict] = []

    def start(self) -> None:
        """Start the profiler."""
        if self._is_profiling:
            return

        self.function_stats = {}
        self.call_stack = []
        self._root_frames = []
        self._current_tree_path = []
        self._is_profiling = True

        if self.track_memory:
            if not tracemalloc.is_tracing():
                tracemalloc.start()

        sys.setprofile(self._profile_handler)

    def stop(self) -> ProfilerResult:
        """Stop the profiler and return the collected results."""
        sys.setprofile(None)
        self._is_profiling = False

        if self.track_memory and tracemalloc.is_tracing():
            # Keep tracing active for multiple sessions? Or stop?
            # Standard practice: we can stop if we are the only one using it.
            pass

        self._results = ProfilerResult(
            function_stats=self.function_stats,
            call_graph=self._root_frames
        )
        return self._results

    def _get_func_stats(self, frame: FrameType) -> FunctionStats:
        code = frame.f_code
        key = f"{code.co_filename}:{code.co_firstlineno}({code.co_name})"
        if key not in self.function_stats:
            self.function_stats[key] = FunctionStats(
                name=code.co_name,
                file_name=code.co_filename,
                line_number=code.co_firstlineno
            )
        return self.function_stats[key]

    def _profile_handler(self, frame: FrameType, event: str, arg: Any) -> None:
        if event == "call":
            self._handle_call(frame)
        elif event == "return":
            self._handle_return(frame)

    def _handle_call(self, frame: FrameType) -> None:
        stats = self._get_func_stats(frame)
        stats.call_count += 1

        mem_usage = 0
        if self.track_memory:
            mem_usage = tracemalloc.get_traced_memory()[0]

        call_frame = CallFrame(
            stats=stats,
            start_time=time.perf_counter(),
            start_memory=mem_usage
        )
        self.call_stack.append(call_frame)

        # Build tree for flame graph
        node = {
            "name": stats.name,
            "full_name": stats.full_name,
            "children": [],
            "start_time": call_frame.start_time
        }

        if not self._current_tree_path:
            self._root_frames.append(node)
        else:
            self._current_tree_path[-1]["children"].append(node)

        self._current_tree_path.append(node)

    def _handle_return(self, frame: FrameType) -> None:
        if not self.call_stack:
            return

        call_frame = self.call_stack.pop()
        end_time = time.perf_counter()
        elapsed = end_time - call_frame.start_time

        stats = call_frame.stats
        stats.total_time += elapsed
        stats.self_time += (elapsed - call_frame.child_time)

        if self.track_memory:
            current_mem = tracemalloc.get_traced_memory()[0]
            mem_diff = current_mem - call_frame.start_memory
            if mem_diff > 0:
                stats.memory_usage = max(stats.memory_usage, mem_diff)

        if self.call_stack:
            self.call_stack[-1].child_time += elapsed

        # Complete tree node
        if self._current_tree_path:
            node = self._current_tree_path.pop()
            node["duration"] = elapsed

    def __enter__(self) -> 'Profiler':
        self.start()
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> None:
        self.stop()

    def profile(self) -> 'Profiler':
        """Enable context manager use."""
        return self

    @staticmethod
    def decorate(func: Callable) -> Callable:
        """Decorator to profile a specific function call and print results."""
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            from .formatter import StatsFormatter
            p = Profiler()
            with p:
                result = func(*args, **kwargs)
            print(f"\n--- Profiling results for {func.__name__} ---", file=sys.stderr)
            print(StatsFormatter.to_table(p._results), file=sys.stderr)
            return result
        return wrapper

    def print_stats(self, sort_by: str = "total_time") -> None:
        """Convenience method to print current stats to stderr."""
        from .formatter import StatsFormatter
        if self._results:
            print(StatsFormatter.to_table(self._results, sort_by=sort_by), file=sys.stderr)

def Profile(func: Callable) -> Callable:
    """Convenience decorator for profiling."""
    return Profiler.decorate(func)
