import pytest
from schemavalidator import validate, ValidationError

def test_empty_schema():
    # An empty schema is always valid
    validate(123, {})
    validate("hello", {})
    validate({"a": 1}, {})
    validate(None, {})

def test_boolean_schemas():
    validate(123, True)
    with pytest.raises(ValidationError):
        validate(123, False)

def test_schema_with_null_value():
    schema = {"type": "null"}
    validate(None, schema)
    with pytest.raises(ValidationError):
        validate(0, schema)
    with pytest.raises(ValidationError):
        validate(False, schema)

def test_large_number():
    # Test with very large numbers
    schema = {"type": "integer", "maximum": 10**20}
    validate(10**20, schema)
    with pytest.raises(ValidationError):
        validate(10**20 + 1, schema)

def test_deeply_nested_instance():
    schema = {
        "type": "object",
        "properties": {
            "a": {"$ref": "#"}
        }
    }
    instance = {"a": {"a": {"a": {"a": {"a": {"a": {"a": {"a": {}}}}}}}}}
    validate(instance, schema)

def test_invalid_ref():
    schema = {"$ref": "#/non/existent"}
    with pytest.raises(ValueError, match=r"Could not resolve \$ref"):
        validate(123, schema)

def test_external_ref_not_supported():
    schema = {"$ref": "http://example.com/schema.json"}
    with pytest.raises(NotImplementedError, match=r"External \$ref not supported"):
        validate(123, schema)
