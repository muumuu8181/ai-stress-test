import pytest
from schemavalidator import validate, ValidationError

def test_number_minimum():
    schema = {"type": "number", "minimum": 10}
    validate(10, schema)
    validate(11.5, schema)
    with pytest.raises(ValidationError):
        validate(9.9, schema)

def test_number_maximum():
    schema = {"type": "number", "maximum": 10}
    validate(10, schema)
    validate(9.5, schema)
    with pytest.raises(ValidationError):
        validate(10.1, schema)

def test_number_exclusiveMinimum():
    schema = {"type": "number", "exclusiveMinimum": 10}
    validate(10.1, schema)
    with pytest.raises(ValidationError):
        validate(10, schema)

def test_number_exclusiveMaximum():
    schema = {"type": "number", "exclusiveMaximum": 10}
    validate(9.9, schema)
    with pytest.raises(ValidationError):
        validate(10, schema)

def test_number_multipleOf():
    schema = {"type": "number", "multipleOf": 2.5}
    validate(5, schema)
    validate(7.5, schema)
    with pytest.raises(ValidationError):
        validate(4, schema)

    # Float precision test
    schema2 = {"type": "number", "multipleOf": 0.1}
    validate(0.3, schema2)

def test_integer_multipleOf():
    schema = {"type": "integer", "multipleOf": 3}
    validate(0, schema)
    validate(6, schema)
    with pytest.raises(ValidationError):
        validate(7, schema)

def test_number_keywords_non_number():
    # Keywords should be ignored if the type is not a number
    schema = {"type": "string", "minimum": 10}
    validate("hello", schema)
