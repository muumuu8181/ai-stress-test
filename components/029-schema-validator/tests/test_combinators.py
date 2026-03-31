import pytest
from schemavalidator import validate, ValidationError

def test_allOf():
    schema = {
        "allOf": [
            {"type": "string", "minLength": 5},
            {"type": "string", "maxLength": 10},
            {"pattern": "^A"}
        ]
    }
    validate("Apple", schema)
    validate("Albatross", schema)
    with pytest.raises(ValidationError):
        validate("Ant", schema) # too short
    with pytest.raises(ValidationError):
        validate("Albatrossss", schema) # too long
    with pytest.raises(ValidationError):
        validate("Bapple", schema) # wrong pattern

def test_anyOf():
    schema = {
        "anyOf": [
            {"type": "string", "maxLength": 5},
            {"type": "number", "minimum": 10}
        ]
    }
    validate("abc", schema)
    validate(11, schema)
    validate(10, schema)
    with pytest.raises(ValidationError):
        validate("abcdef", schema) # too long and not number
    with pytest.raises(ValidationError):
        validate(5, schema) # too small and not string

def test_oneOf():
    schema = {
        "oneOf": [
            {"type": "number", "multipleOf": 5},
            {"type": "number", "multipleOf": 3}
        ]
    }
    validate(5, schema)
    validate(3, schema)
    validate(9, schema)
    with pytest.raises(ValidationError):
        validate(15, schema) # matches both
    with pytest.raises(ValidationError):
        validate(7, schema) # matches none

def test_not():
    schema = {"not": {"type": "string"}}
    validate(123, schema)
    validate({"a": 1}, schema)
    with pytest.raises(ValidationError):
        validate("hello", schema)
