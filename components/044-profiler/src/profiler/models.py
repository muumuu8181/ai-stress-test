from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FunctionStats:
    """Statistics for a single function."""
    name: str
    file_name: str
    line_number: int
    call_count: int = 0
    total_time: float = 0.0  # Cumulative time (including sub-calls)
    self_time: float = 0.0   # Self time (excluding sub-calls)
    memory_usage: int = 0    # Peak memory usage in bytes during this function (if tracked)

    def __post_init__(self):
        self.full_name = f"{self.file_name}:{self.line_number}({self.name})"


@dataclass
class CallFrame:
    """Represents a frame in the call stack during profiling."""
    stats: FunctionStats
    start_time: float
    start_memory: int = 0
    child_time: float = 0.0

@dataclass
class ProfilerResult:
    """Results of a profiling session."""
    function_stats: Dict[str, FunctionStats]
    call_graph: List[Dict] # For flame graph / stack representation
