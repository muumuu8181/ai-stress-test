from typing import List, Tuple, TypeVar, Optional, Dict
from .lcs import get_lcs_matrix
import os

T = TypeVar("T")

class DiffOp:
    """Represents a diff operation: keep (equal), insert, or delete."""
    EQUAL = " "
    INSERT = "+"
    DELETE = "-"

    def __init__(self, op: str, value: T):
        self.op = op
        self.value = value

    def __repr__(self) -> str:
        return f"{self.op} {self.value}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DiffOp):
            return False
        return self.op == other.op and self.value == other.value

def get_diff(a: List[T], b: List[T]) -> List[DiffOp]:
    """
    Computes the difference between two sequences using LCS.

    Args:
        a: The source sequence.
        b: The target sequence.

    Returns:
        A list of DiffOp objects.
    """
    dp = get_lcs_matrix(a, b)
    diff = []
    i, j = len(a), len(b)

    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i-1] == b[j-1]:
            diff.append(DiffOp(DiffOp.EQUAL, a[i-1]))
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j-1] >= dp[i-1][j]):
            diff.append(DiffOp(DiffOp.INSERT, b[j-1]))
            j -= 1
        elif i > 0 and (j == 0 or dp[i][j-1] < dp[i-1][j]):
            diff.append(DiffOp(DiffOp.DELETE, a[i-1]))
            i -= 1

    return diff[::-1]

def get_line_diff(source: str, target: str) -> List[DiffOp]:
    """
    Computes line-level differences between two strings.

    Args:
        source: The source string.
        target: The target string.

    Returns:
        A list of DiffOp objects representing line changes.
    """
    a_lines = source.splitlines(keepends=True)
    b_lines = target.splitlines(keepends=True)
    return get_diff(a_lines, b_lines)

def get_inline_diff(source: str, target: str) -> List[DiffOp]:
    """
    Computes character-level (inline) differences between two strings.

    Args:
        source: The source string.
        target: The target string.

    Returns:
        A list of DiffOp objects representing character changes.
    """
    return get_diff(list(source), list(target))

def get_directory_diff(dir_a: str, dir_b: str) -> Dict[str, str]:
    """
    Computes differences between two directories recursively.

    Args:
        dir_a: Path to the first directory.
        dir_b: Path to the second directory.

    Returns:
        A dictionary mapping file paths to their status (only in A, only in B, or modified).
    """
    diffs = {}

    files_a = set()
    for root, _, files in os.walk(dir_a):
        for f in files:
            files_a.add(os.path.relpath(os.path.join(root, f), dir_a))

    files_b = set()
    for root, _, files in os.walk(dir_b):
        for f in files:
            files_b.add(os.path.relpath(os.path.join(root, f), dir_b))

    only_a = files_a - files_b
    only_b = files_b - files_a
    common = files_a & files_b

    for f in only_a:
        diffs[f] = "only in source"
    for f in only_b:
        diffs[f] = "only in target"
    for f in common:
        path_a = os.path.join(dir_a, f)
        path_b = os.path.join(dir_b, f)
        with open(path_a, "r", encoding="utf-8") as fa, open(path_b, "r", encoding="utf-8") as fb:
            if fa.read() != fb.read():
                diffs[f] = "modified"

    return diffs
