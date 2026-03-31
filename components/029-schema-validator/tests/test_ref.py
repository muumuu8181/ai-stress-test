import pytest
from schemavalidator import validate, ValidationError

def test_ref_internal():
    schema = {
        "definitions": {
            "positiveInteger": {"type": "integer", "minimum": 0}
        },
        "type": "object",
        "properties": {
            "age": {"$ref": "#/definitions/positiveInteger"}
        }
    }
    validate({"age": 30}, schema)
    with pytest.raises(ValidationError):
        validate({"age": -1}, schema)

def test_ref_recursive():
    schema = {
        "definitions": {
            "node": {
                "type": "object",
                "properties": {
                    "value": {"type": "integer"},
                    "next": {"$ref": "#/definitions/node"}
                },
                "required": ["value"]
            }
        },
        "$ref": "#/definitions/node"
    }
    instance = {
        "value": 1,
        "next": {
            "value": 2,
            "next": {
                "value": 3
            }
        }
    }
    validate(instance, schema)
    with pytest.raises(ValidationError):
        invalid_instance = {
            "value": 1,
            "next": {
                "value": "two"
            }
        }
        validate(invalid_instance, schema)

def test_ref_root():
    schema = {
        "type": "object",
        "properties": {
            "child": {"$ref": "#"}
        }
    }
    validate({"child": {"child": {}}}, schema)
    with pytest.raises(ValidationError):
        validate({"child": 123}, schema)

def test_ref_pointer_encoding():
    schema = {
        "definitions": {
            "foo/bar": {"type": "string"},
            "foo~bar": {"type": "integer"}
        },
        "type": "object",
        "properties": {
            "a": {"$ref": "#/definitions/foo~1bar"},
            "b": {"$ref": "#/definitions/foo~0bar"}
        }
    }
    validate({"a": "hello", "b": 123}, schema)
    with pytest.raises(ValidationError):
        validate({"a": 123}, schema)

def test_ref_infinite_recursion_guard():
    # This should not raise RecursionError but simply return (as per guard)
    schema = {"$ref": "#"}
    validate(123, schema)
