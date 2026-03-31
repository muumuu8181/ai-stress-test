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
        return (current, False)
    if current == ancestor:
        return (other, False)
    if other == ancestor:
        return (current, False)

    a_lines = ancestor.splitlines(keepends=True)
    b_lines = current.splitlines(keepends=True)
    o_lines = other.splitlines(keepends=True)

    diff_b = get_diff(a_lines, b_lines)
    diff_o = get_diff(a_lines, o_lines)

    def process_diff(orig: List[str], diff_ops: List[DiffOp]) -> List[Tuple[bool, List[str]]]:
        # results[i] = (is_kept, [inserted_lines_AFTER])
        # size len(orig)
        results = [[False, []] for _ in range(len(orig))]
        inserts_before = []

        orig_idx = 0
        for op in diff_ops:
            if op.op == DiffOp.EQUAL:
                results[orig_idx][0] = True
                orig_idx += 1
            elif op.op == DiffOp.DELETE:
                # remains False
                orig_idx += 1
            elif op.op == DiffOp.INSERT:
                if orig_idx == 0:
                    inserts_before.append(op.value)
                else:
                    results[orig_idx-1][1].append(op.value)
        return inserts_before, results

    ins_before_b, fates_b = process_diff(a_lines, diff_b)
    ins_before_o, fates_o = process_diff(a_lines, diff_o)

    result_lines = []
    has_conflicts = False

    # Merge insertions before the first line
    if ins_before_b == ins_before_o:
        result_lines.extend(ins_before_b)
    elif not ins_before_b:
        result_lines.extend(ins_before_o)
    elif not ins_before_o:
        result_lines.extend(ins_before_b)
    else:
        has_conflicts = True
        result_lines.append("<<<<<<< CURRENT\n")
        result_lines.extend(ins_before_b)
        result_lines.append("=======\n")
        result_lines.extend(ins_before_o)
        result_lines.append(">>>>>>> OTHER\n")

    for i in range(len(a_lines)):
        kept_b, ins_b = fates_b[i]
        kept_o, ins_o = fates_o[i]

        # Original line i
        if kept_b and kept_o:
            result_lines.append(a_lines[i])
        elif not kept_b and not kept_o:
            # Both deleted it or modified it.
            # A modification is if ins is not empty.
            if ins_b != ins_o:
                # If they modified it differently, or one modified and other deleted (empty ins), it's a conflict!
                has_conflicts = True
                result_lines.append("<<<<<<< CURRENT\n")
                result_lines.extend(ins_b)
                result_lines.append("=======\n")
                result_lines.extend(ins_o)
                result_lines.append(">>>>>>> OTHER\n")
                # Important: skip the ins below because we just added them in conflict markers
                continue
            else:
                # Both modified it identically, or both deleted it (empty ins)
                pass
        elif kept_b and not kept_o:
            # B kept it unchanged, O deleted or modified it.
            # Take O's action (nothing if deleted, or modified content)
            pass
        elif not kept_b and kept_o:
            # O kept it unchanged, B deleted or modified it.
            pass

        # Merge insertions AFTER line i (which is actually the modification content or actual additions)
        if ins_b == ins_o:
            result_lines.extend(ins_b)
        elif not ins_b:
            result_lines.extend(ins_o)
        elif not ins_o:
            result_lines.extend(ins_b)
        else:
            has_conflicts = True
            result_lines.append("<<<<<<< CURRENT\n")
            result_lines.extend(ins_b)
            result_lines.append("=======\n")
            result_lines.extend(ins_o)
            result_lines.append(">>>>>>> OTHER\n")

    return ("".join(result_lines), has_conflicts)
