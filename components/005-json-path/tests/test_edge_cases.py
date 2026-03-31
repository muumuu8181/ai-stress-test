import pytest
from jsonpath import find, update, delete

def test_empty_input():
    assert find({}, "$") == [{}]
    assert find([], "$") == [[]]
    assert find({}, "$.foo") == []
    assert find([], "$[0]") == []

def test_null_input():
    assert find(None, "$") == [None]
    assert find(None, "$.foo") == []

def test_invalid_path():
    with pytest.raises(ValueError):
        find({"a": 1}, ".a")  # No root

def test_deeply_nested():
    data = {"a": {"b": {"c": {"d": 42}}}}
    assert find(data, "$.a.b.c.d") == [42]
    assert find(data, "$..d") == [42]

def test_array_out_of_bounds():
    data = {"list": [1, 2, 3]}
    assert find(data, "$.list[5]") == []

def test_non_existent_field():
    data = {"a": 1}
    assert find(data, "$.b") == []

def test_filter_non_existent_field():
    data = {"list": [{"a": 1}, {"b": 2}]}
    # Evaluation of @.a should return None for the second item, and 1 < 10 for the first.
    # None < 10 should be handled without crashing.
    assert find(data, "$.list[?(@.a < 10)]") == [{"a": 1}]

def test_script_length():
    data = [1, 2, 3, 4, 5, 6]
    assert find(data, "$[?(@.length > 5)]") == [[1, 2, 3, 4, 5, 6]]

    data2 = {"items": ["abc", "abcdef"]}
    assert find(data2, "$.items[?(@.length > 5)]") == ["abcdef"]

def test_delete_root():
    # Deleting root isn't supported as it has no parent
    data = {"a": 1}
    delete(data, "$")
    assert data == {"a": 1}
