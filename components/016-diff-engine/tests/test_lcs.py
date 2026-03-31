import pytest
from diffengine.lcs import get_lcs, get_lcs_matrix

def test_get_lcs_basic():
    assert get_lcs("abc", "abc") == list("abc")
    assert get_lcs("abc", "def") == []
    assert get_lcs("abcde", "ace") == list("ace")
    assert get_lcs("ace", "abcde") == list("ace")

def test_get_lcs_empty():
    assert get_lcs("", "") == []
    assert get_lcs("abc", "") == []
    assert get_lcs("", "abc") == []

def test_get_lcs_matrix():
    a = "abc"
    b = "ac"
    matrix = get_lcs_matrix(list(a), list(b))
    assert len(matrix) == 4
    assert len(matrix[0]) == 3
    assert matrix[3][2] == 2  # LCS("abc", "ac") length is 2

def test_get_lcs_with_lists():
    a = ["line1\n", "line2\n"]
    b = ["line1\n", "line3\n"]
    assert get_lcs(a, b) == ["line1\n"]
