import pytest
from schemavalidator import validate, ValidationError

def test_object_required():
    schema = {"type": "object", "required": ["name", "age"]}
    validate({"name": "Alice", "age": 30}, schema)
    validate({"name": "Alice", "age": 30, "extra": True}, schema)
    with pytest.raises(ValidationError):
        validate({"name": "Alice"}, schema)

def test_object_minProperties():
    schema = {"type": "object", "minProperties": 2}
    validate({"a": 1, "b": 2}, schema)
    with pytest.raises(ValidationError):
        validate({"a": 1}, schema)

def test_object_maxProperties():
    schema = {"type": "object", "maxProperties": 2}
    validate({"a": 1, "b": 2}, schema)
    with pytest.raises(ValidationError):
        validate({"a": 1, "b": 2, "c": 3}, schema)

def test_object_properties():
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0}
        }
    }
    validate({"name": "Alice", "age": 30}, schema)
    validate({"extra": 123}, schema) # extra is allowed
    with pytest.raises(ValidationError):
        validate({"name": 123}, schema)

def test_object_additionalProperties_false():
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        },
        "additionalProperties": False
    }
    validate({"name": "Alice"}, schema)
    with pytest.raises(ValidationError):
        validate({"name": "Alice", "extra": 123}, schema)

def test_object_additionalProperties_schema():
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}
        },
        "additionalProperties": {"type": "integer"}
    }
    validate({"name": "Alice", "extra": 123, "another": 456}, schema)
    with pytest.raises(ValidationError):
        validate({"name": "Alice", "extra": "not-int"}, schema)

def test_object_json_path():
    schema = {
        "type": "object",
        "properties": {
            "nested": {
                "type": "object",
                "properties": {
                    "list": {
                        "type": "array",
                        "items": {"type": "integer"}
                    }
                }
            }
        }
    }
    instance = {"nested": {"list": [1, "two", 3]}}
    with pytest.raises(ValidationError) as exc_info:
        validate(instance, schema)
    assert exc_info.value.json_path == "$.nested.list[1]"
