import pytest
from regexengine import match, search

def test_shorthand_in_char_class():
    assert match("[\\d]+", "123").group() == "123"
    assert match("[\\d]+", "abc") is None
    # assert match("[a-\\d]", "0").group() == "0" # This was a bad test case
    assert match("[\\w]+", "abc_123").group() == "abc_123"
    assert match("[\\s]+", " \t").group() == " \t"

def test_mixed_char_class():
    assert match("[a-z\\d_]+", "abc_123").group() == "abc_123"
    assert match("[^\\d]+", "abc").group() == "abc"
    assert match("[^\\d]+", "123") is None
