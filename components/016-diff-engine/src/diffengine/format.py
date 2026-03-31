from typing import List, Dict, Tuple
from .diff import DiffOp

def format_unified(ops: List[DiffOp], source_file: str = "source", target_file: str = "target", context: int = 3) -> str:
    """
    Formats a list of DiffOp objects into the Unified Diff format with hunks and context.

    Args:
        ops: List of DiffOp objects.
        source_file: Name of the source file.
        target_file: Name of the target file.
        context: Number of context lines.

    Returns:
        A string in Unified Diff format.
    """
    if not any(op.op != DiffOp.EQUAL for op in ops):
        return f"--- {source_file}\n+++ {target_file}\n"

    lines = []
    lines.append(f"--- {source_file}\n")
    lines.append(f"+++ {target_file}\n")

    changed_indices = [i for i, op in enumerate(ops) if op.op != DiffOp.EQUAL]

    if not changed_indices:
        return "".join(lines)

    hunk_ranges = []
    if changed_indices:
        start = max(0, changed_indices[0] - context)
        end = min(len(ops), changed_indices[0] + context + 1)

        for i in range(1, len(changed_indices)):
            idx = changed_indices[i]
            if idx - context < end:
                end = min(len(ops), idx + context + 1)
            else:
                hunk_ranges.append((start, end))
                start = max(0, idx - context)
                end = min(len(ops), idx + context + 1)
        hunk_ranges.append((start, end))

    # Pre-calculate line numbers
    op_line_nums = []
    s, t = 1, 1
    for op in ops:
        op_line_nums.append((s, t))
        if op.op == DiffOp.EQUAL:
            s += 1
            t += 1
        elif op.op == DiffOp.DELETE:
            s += 1
        elif op.op == DiffOp.INSERT:
            t += 1

    for start, end in hunk_ranges:
        hunk_ops = ops[start:end]
        s_start, t_start = op_line_nums[start]
        s_count = sum(1 for op in hunk_ops if op.op != DiffOp.INSERT)
        t_count = sum(1 for op in hunk_ops if op.op != DiffOp.DELETE)

        lines.append(f"@@ -{s_start},{s_count} +{t_start},{t_count} @@\n")

        for op in hunk_ops:
            val = op.value
            if not val.endswith('\n'):
                val += '\n'
            if op.op == DiffOp.EQUAL:
                lines.append(f" {val}")
            elif op.op == DiffOp.DELETE:
                lines.append(f"-{val}")
            elif op.op == DiffOp.INSERT:
                lines.append(f"+{val}")

    return "".join(lines)

def format_side_by_side(ops: List[DiffOp], width: int = 40) -> str:
    """
    Formats a list of DiffOp objects into a side-by-side display.

    Args:
        ops: List of DiffOp objects.
        width: Width of each column.

    Returns:
        A string representing the side-by-side diff.
    """
    lines = []

    # Process ops to group DELETE and INSERT into modifications
    i = 0
    while i < len(ops):
        op = ops[i]
        left = ""
        right = ""

        if op.op == DiffOp.EQUAL:
            val = op.value.rstrip('\r\n') if isinstance(op.value, str) else str(op.value)
            left = val
            right = val
            sep = "  "
            i += 1
        elif op.op == DiffOp.DELETE:
            left = op.value.rstrip('\r\n') if isinstance(op.value, str) else str(op.value)
            # Check if next is INSERT to show as change
            if i + 1 < len(ops) and ops[i+1].op == DiffOp.INSERT:
                right = ops[i+1].value.rstrip('\r\n') if isinstance(ops[i+1].value, str) else str(ops[i+1].value)
                sep = " |"
                i += 2
            else:
                right = ""
                sep = " <"
                i += 1
        elif op.op == DiffOp.INSERT:
            left = ""
            right = op.value.rstrip('\r\n') if isinstance(op.value, str) else str(op.value)
            sep = " >"
            i += 1

        left_trunc = left[:width].ljust(width)
        right_trunc = right[:width].ljust(width)
        lines.append(f"{left_trunc}{sep}{right_trunc}")

    return "\n".join(lines)

def get_diff_stats(ops: List[DiffOp]) -> Dict[str, int]:
    """
    Computes diff statistics (added, deleted, changed).

    Args:
        ops: List of DiffOp objects.

    Returns:
        A dictionary with counts for 'added', 'deleted', and 'changed'.
    """
    stats = {"added": 0, "deleted": 0, "changed": 0}

    i = 0
    while i < len(ops):
        op = ops[i]
        if op.op == DiffOp.DELETE:
            if i + 1 < len(ops) and ops[i+1].op == DiffOp.INSERT:
                stats["changed"] += 1
                i += 2
            else:
                stats["deleted"] += 1
                i += 1
        elif op.op == DiffOp.INSERT:
            stats["added"] += 1
            i += 1
        else:
            i += 1

    return stats
