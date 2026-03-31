import pytest
from regexengine import match, search, findall, sub

def test_match_simple():
    assert match("abc", "abcdef").group() == "abc"
    assert match("abc", "xabcdef") is None

def test_search_simple():
    assert search("abc", "xabcdef").group() == "abc"
    assert search("abc", "xabxdef") is None

def test_dot():
    assert match("a.c", "abc").group() == "abc"
    assert match("a.c", "a\nc") is None

def test_anchors():
    assert search("^abc", "abc") is not None
    assert search("^abc", "xabc") is None
    assert search("abc$", "abc") is not None
    assert search("abc$", "abcd") is None

def test_quantifiers():
    assert match("a*", "aaa").group() == "aaa"
    assert match("a*", "").group() == ""
    assert match("a+", "aaa").group() == "aaa"
    assert match("a+", "") is None
    assert match("a?", "a").group() == "a"
    assert match("a?", "").group() == ""

def test_braces():
    assert match("a{2,3}", "aa").group() == "aa"
    assert match("a{2,3}", "aaa").group() == "aaa"
    assert match("a{2,3}", "aaaa").group() == "aaa"
    assert match("a{2,3}", "a") is None

def test_alternation():
    assert match("a|b", "a").group() == "a"
    assert match("a|b", "b").group() == "b"
    assert match("a|b", "c") is None

def test_char_class():
    assert match("[abc]", "a").group() == "a"
    assert match("[a-z]", "m").group() == "m"
    assert match("[^abc]", "d").group() == "d"
    assert match("[^abc]", "a") is None

def test_special_escapes():
    assert match(r"\d+", "123").group() == "123"
    assert match(r"\w+", "abc_123").group() == "abc_123"
    assert match(r"\s+", "  \t\n").group() == "  \t\n"

def test_groups():
    m = match("(abc)def", "abcdef")
    assert m.group(1) == "abc"
    assert m.groups() == ("abc",)

def test_findall():
    assert findall(r"\d+", "12abc34def56") == ["12", "34", "56"]
    assert findall(r"(\d)(\d)", "1234") == [("1", "2"), ("3", "4")]

def test_sub():
    assert sub(r"\d+", "NUM", "12abc34") == "NUMabcNUM"
    assert sub(r"(\d)(\d)", r"\2\1", "1234") == "2143"
    assert sub(r"a", "b", "aaaaa", count=2) == "bbaaa"

def test_callable_sub():
    def repl(m):
        return str(int(m.group(0)) * 2)
    assert sub(r"\d+", repl, "10 20 30") == "20 40 60"
