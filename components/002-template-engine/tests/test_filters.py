import pytest
from templateengine.filters import upper_filter, currency_filter, join_filter, safe_filter, SafeString

def test_upper_filter():
    assert upper_filter("hello") == "HELLO"
    assert upper_filter(123) == "123"

def test_currency_filter():
    assert currency_filter(100.5) == "$100.50"
    assert currency_filter("1000") == "$1,000.00"
    assert currency_filter("abc") == "abc"

def test_join_filter():
    assert join_filter([1, 2, 3]) == "1, 2, 3"
    assert join_filter(["a", "b"], " | ") == "a | b"
    assert join_filter("test") == "test"

def test_safe_filter():
    result = safe_filter("<br>")
    assert isinstance(result, SafeString)
    assert result == "<br>"
    assert result.__html__() == "<br>"
