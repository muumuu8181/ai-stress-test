# 044-profiler: Python Code Profiler

A lightweight Python code profiler using only the standard library.

## Features

- Function-level profiling with call count, cumulative time, and self time.
- Memory usage tracking (using `tracemalloc`).
- Context manager support: `with profiler.profile():`.
- Decorator support: `@Profile`.
- Statistics output: Plain text Table, JSON, and text-based Flame graph.
- Sorting and filtering (regex).

## Usage

### Basic Profiling (Context Manager)

```python
from profiler import Profiler, StatsFormatter

p = Profiler(track_memory=True)
with p:
    # Code to profile
    my_expensive_function()

results = p.stop()
print(StatsFormatter.to_table(results))
```

### Decorator

```python
from profiler import Profile

@Profile
def my_function():
    # Profiling will start and stop automatically for this call.
    pass
```

### Statistics Formatting

```python
results = p.stop()

# Table output
print(StatsFormatter.to_table(results, sort_by="total_time", filter_pattern="^my_"))

# JSON output
print(StatsFormatter.to_json(results))

# Flame graph (folded stack format)
with open("flame.txt", "w") as f:
    f.write(StatsFormatter.to_flamegraph(results))
```

## Supported Sort Keys

- `total_time` (default)
- `self_time`
- `call_count`
- `memory_usage`
- `name`

## Testing

Run tests with `pytest`:

```bash
PYTHONPATH=src pytest tests/
```
