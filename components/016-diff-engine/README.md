# Diff Engine

A robust difference engine implemented in pure Python.

## Features

- **LCS-based Line Diff**: Finds the longest common subsequence to determine line changes.
- **Inline Diff**: Character-level differences for granular change analysis.
- **Unified Diff Format**: Standard output format for patches.
- **Side-by-side Display**: Visual comparison of two versions.
- **Diff Statistics**: Counts of added, deleted, and changed lines.
- **Patch Application**: Apply patches to reconstruct target files.
- **3-way Merge**: Combine changes from two branches based on a common ancestor.
- **Directory Diff**: Recursive comparison of directory structures and file contents.

## Installation

This package requires Python 3.7+ and has no external dependencies.

## Usage

### Line-level Diff

```python
from diffengine.diff import get_line_diff
from diffengine.format import format_unified

source = "line1\nline2\n"
target = "line1\nline3\n"
diff = get_line_diff(source, target)
print(format_unified(diff))
```

### Side-by-side Display

```python
from diffengine.diff import get_line_diff
from diffengine.format import format_side_by_side

diff = get_line_diff(source, target)
print(format_side_by_side(diff, width=30))
```

### Patching

```python
from diffengine.patch import apply_unified_patch

patch = format_unified(diff)
restored = apply_unified_patch(source, patch)
```

### 3-way Merge

```python
from diffengine.merge import merge_3way

ancestor = "base content"
current = "my changes"
other = "their changes"
merged, conflict = merge_3way(ancestor, current, other)
```

### Directory Diff

```python
from diffengine.diff import get_directory_diff

diffs = get_directory_diff("dir_a", "dir_b")
for path, status in diffs.items():
    print(f"{path}: {status}")
```

## Testing

Run tests using pytest:

```bash
pytest tests/
```

To check coverage:

```bash
pytest --cov=diffengine tests/
```
