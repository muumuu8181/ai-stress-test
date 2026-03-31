import pytest
from schemavalidator import validate, ValidationError

def test_string_type():
    validate("hello", {"type": "string"})
    with pytest.raises(ValidationError):
        validate(123, {"type": "string"})

def test_number_type():
    validate(123.45, {"type": "number"})
    validate(123, {"type": "number"})
    with pytest.raises(ValidationError):
        validate("123", {"type": "number"})

def test_integer_type():
    validate(123, {"type": "integer"})
    with pytest.raises(ValidationError):
        validate(123.45, {"type": "integer"})

def test_boolean_type():
    validate(True, {"type": "boolean"})
    validate(False, {"type": "boolean"})
    with pytest.raises(ValidationError):
        validate("True", {"type": "boolean"})

def test_array_type():
    validate([1, 2, 3], {"type": "array"})
    with pytest.raises(ValidationError):
        validate({"a": 1}, {"type": "array"})

def test_object_type():
    validate({"a": 1}, {"type": "object"})
    with pytest.raises(ValidationError):
        validate([1, 2, 3], {"type": "object"})

def test_null_type():
    validate(None, {"type": "null"})
    with pytest.raises(ValidationError):
        validate(0, {"type": "null"})

def test_multiple_types():
    schema = {"type": ["string", "integer"]}
    validate("hello", schema)
    validate(123, schema)
    with pytest.raises(ValidationError):
        validate(1.2, schema)

def test_no_type():
    # If type is not specified, everything is valid for that keyword
    validate(123, {})
    validate("hello", {})
