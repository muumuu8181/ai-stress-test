import pytest
from schemavalidator import validate, ValidationError

def test_array_minItems():
    schema = {"type": "array", "minItems": 2}
    validate([1, 2], schema)
    with pytest.raises(ValidationError):
        validate([1], schema)

def test_array_maxItems():
    schema = {"type": "array", "maxItems": 3}
    validate([1, 2, 3], schema)
    with pytest.raises(ValidationError):
        validate([1, 2, 3, 4], schema)

def test_array_uniqueItems():
    schema = {"type": "array", "uniqueItems": True}
    validate([1, 2, 3], schema)
    validate(["a", "b", "c"], schema)
    validate([{"a": 1}, {"a": 2}], schema)
    # Boolean vs integer distinction
    validate([True, 1], schema)
    validate([False, 0], schema)
    with pytest.raises(ValidationError):
        validate([1, 2, 1], schema)
    with pytest.raises(ValidationError):
        validate([{"a": 1}, {"a": 1}], schema)
    with pytest.raises(ValidationError):
        validate([True, True], schema)

def test_array_items_schema():
    schema = {"type": "array", "items": {"type": "integer", "minimum": 10}}
    validate([10, 11, 20], schema)
    with pytest.raises(ValidationError):
        validate([10, 9, 20], schema)

def test_array_items_list():
    schema = {"type": "array", "items": [{"type": "string"}, {"type": "number"}]}
    validate(["hello", 123], schema)
    validate(["hello", 123, True], schema) # additional items allowed by default
    with pytest.raises(ValidationError):
        validate([123, "hello"], schema)

def test_array_contains():
    schema = {"type": "array", "contains": {"type": "integer", "minimum": 100}}
    validate([1, 100, 2], schema)
    validate([200, 300], schema)
    with pytest.raises(ValidationError):
        validate([1, 2, 3], schema)
