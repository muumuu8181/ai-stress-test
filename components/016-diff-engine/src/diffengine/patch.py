from typing import List
from .diff import DiffOp
import re

def apply_patch(source: str, diff_ops: List[DiffOp]) -> str:
    """
    Applies a list of DiffOp objects to a source string to reconstruct the target string.

    Args:
        source: The source string.
        diff_ops: List of DiffOp objects.

    Returns:
        The target string.
    """
    result = []
    for op in diff_ops:
        if op.op == DiffOp.EQUAL:
            result.append(op.value)
        elif op.op == DiffOp.INSERT:
            result.append(op.value)
        elif op.op == DiffOp.DELETE:
            pass

    return "".join(result)

def apply_unified_patch(source: str, patch: str) -> str:
    """
    Applies a Unified Diff patch to a source string.
    Handles multiple hunks and line numbers.

    Args:
        source: The source string.
        patch: The Unified Diff patch string.

    Returns:
        The target string.
    """
    source_lines = source.splitlines(keepends=True)
    patch_lines = patch.splitlines(keepends=True)

    result_lines = list(source_lines)
    offset = 0

    i = 0
    while i < len(patch_lines):
        line = patch_lines[i]
        if line.startswith('@@'):
            # Parse @@ -s,n +t,m @@
            match = re.search(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
            if not match:
                i += 1
                continue

            s_start = int(match.group(1))
            s_count = int(match.group(2)) if match.group(2) is not None else 1
            t_start = int(match.group(3))
            t_count = int(match.group(4)) if match.group(4) is not None else 1

            i += 1
            hunk_target_lines = []

            while i < len(patch_lines) and not (patch_lines[i].startswith('@@') or
                                               patch_lines[i].startswith('---') or
                                               patch_lines[i].startswith('+++')):
                pline = patch_lines[i]
                if pline.startswith(' '):
                    hunk_target_lines.append(pline[1:])
                elif pline.startswith('+'):
                    hunk_target_lines.append(pline[1:])
                elif pline.startswith('-'):
                    pass # Skip deleted lines for target
                i += 1

            # Apply the hunk
            start_idx = s_start - 1 + offset
            end_idx = start_idx + s_count

            # Replace the lines in source with target lines from hunk
            result_lines[start_idx:end_idx] = hunk_target_lines

            # Update offset for next hunks
            offset += (len(hunk_target_lines) - s_count)
        else:
            i += 1

    return "".join(result_lines)
