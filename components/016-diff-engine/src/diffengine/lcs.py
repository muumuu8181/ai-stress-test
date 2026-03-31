from typing import List, TypeVar

T = TypeVar("T")

def get_lcs_matrix(a: List[T], b: List[T]) -> List[List[int]]:
    """
    Computes the LCS (Longest Common Subsequence) length matrix for two sequences.

    Args:
        a: The first sequence.
        b: The second sequence.

    Returns:
        A 2D list where dp[i][j] is the length of the LCS of a[:i] and b[:j].
    """
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp

def get_lcs(a: List[T], b: List[T]) -> List[T]:
    """
    Returns the Longest Common Subsequence of two sequences.

    Args:
        a: The first sequence.
        b: The second sequence.

    Returns:
        The longest common subsequence as a list.
    """
    dp = get_lcs_matrix(a, b)
    lcs = []
    i, j = len(a), len(b)
    while i > 0 and j > 0:
        if a[i-1] == b[j-1]:
            lcs.append(a[i-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    return lcs[::-1]
