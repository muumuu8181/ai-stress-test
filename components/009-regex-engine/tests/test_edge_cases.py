import pytest
from regexengine import match, search, compile

def test_empty_pattern():
    assert match("", "abc").group() == ""
    assert match("", "").group() == ""

def test_empty_string():
    assert match("abc", "") is None
    assert match("a*", "").group() == ""

def test_invalid_pattern():
    with pytest.raises(ValueError):
        compile("(abc")
    with pytest.raises(ValueError):
        compile("[abc")
    with pytest.raises(ValueError):
        compile("a{x}")

def test_large_quantifier():
    assert match("a{10}", "aaaaaaaaaa").group() == "aaaaaaaaaa"
    assert match("a{10}", "aaaaaaaaa") is None

def test_nested_groups():
    m = match("((a)b)", "ab")
    assert m.group(0) == "ab"
    assert m.group(1) == "ab"
    assert m.group(2) == "a"

def test_backtracking_like_behavior():
    # Standard NFA handles this without backtracking
    assert match("a*a", "aaaa").group() == "aaaa"
    assert match("(a|ab)c", "abc").group() == "abc"

def test_overlapping_matches_search():
    # search should find the first occurrence
    assert search("aba", "ababa").group() == "aba"
    assert search("aba", "ababa").start() == 0

def test_caret_not_at_start():
    # ^ only matches at position 0
    assert search("^b", "ab") is None
    assert search("a^b", "ab") is None # Impossible match in most engines

def test_dollar_not_at_end():
    # $ only matches at end
    assert search("a$", "ab") is None
    assert search("a$b", "ab") is None # Impossible
