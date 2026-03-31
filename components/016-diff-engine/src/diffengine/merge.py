from typing import List, Tuple, Optional
from .diff import get_diff, DiffOp

def merge_3way(ancestor: str, current: str, other: str) -> Tuple[str, bool]:
    """
    Performs a 3-way merge of two modified versions of a common ancestor.

    Args:
        ancestor: The common ancestor string.
        current: The first modified version.
        other: The second modified version.

    Returns:
        A tuple of (merged string, has_conflicts boolean).
    """
    if current == other:
        return current, False
    if current == ancestor:
        return other, False
    if other == ancestor:
        return current, False

    a_lines = ancestor.splitlines(keepends=True)
    b_lines = current.splitlines(keepends=True)
    o_lines = other.splitlines(keepends=True)

    # Simplified 3-way merge on lines
    # We'll use get_diff from ancestor to current and ancestor to other
    diff_b = get_diff(a_lines, b_lines)
    diff_o = get_diff(a_lines, o_lines)

    # We need a unified view of what happened to each line of ancestor.
    # Each ancestor line index i can have:
    # 1. Associated insertions before it (list of lines)
    # 2. Status: kept, deleted

    def process_diff(orig: List[str], diff_ops: List[DiffOp]) -> List[Tuple[List[str], bool]]:
        # Returns a list of (insertions, is_kept) for each original line,
        # plus one for insertions at the end.
        results = [([], True) for _ in range(len(orig) + 1)]
        orig_idx = 0
        for op in diff_ops:
            if op.op == DiffOp.EQUAL:
                orig_idx += 1
            elif op.op == DiffOp.DELETE:
                results[orig_idx] = (results[orig_idx][0], False)
                orig_idx += 1
            elif op.op == DiffOp.INSERT:
                results[orig_idx][0].append(op.value)
        return results

    state_b = process_diff(a_lines, diff_b)
    state_o = process_diff(a_lines, diff_o)

    result_lines = []
    has_conflicts = False

    for i in range(len(a_lines) + 1):
        ins_b, kept_b = state_b[i]
        ins_o, kept_o = state_o[i]

        # Merge insertions
        if ins_b == ins_o:
            result_lines.extend(ins_b)
        elif not ins_b:
            result_lines.extend(ins_o)
        elif not ins_o:
            result_lines.extend(ins_b)
        else:
            # Conflict in insertions
            has_conflicts = True
            result_lines.append("<<<<<<< CURRENT\n")
            result_lines.extend(ins_b)
            result_lines.append("=======\n")
            result_lines.extend(ins_o)
            result_lines.append(">>>>>>> OTHER\n")

        # Merge original line
        if i < len(a_lines):
            if kept_b and kept_o:
                result_lines.append(a_lines[i])
            elif not kept_b and not kept_o:
                pass # Both deleted
            elif kept_b and not kept_o:
                pass # o deleted it, b kept it -> delete it
            elif not kept_b and kept_o:
                pass # b deleted it, o kept it -> delete it
            # Actually, standard merge: if one side deletes and other side keeps UNCHANGED, it's delete.
            # If one side deletes and other side modifies, it's conflict.
            # Our model of "kept_b" only means it was EQUAL in the diff.
            # If it was changed, it would be DELETE + INSERT in the diff.
            # So if kept_b is true, the line is unchanged from ancestor.

    return "".join(result_lines), has_conflicts
