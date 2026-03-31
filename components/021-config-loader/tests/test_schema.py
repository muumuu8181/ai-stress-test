import pytest
from config_loader.schema import Validator, SchemaField, ValidationError

def test_schema_basic():
    schema = {
        "host": SchemaField(str, required=True),
        "port": SchemaField(int, default=8080, min_val=0, max_val=65535),
        "debug": SchemaField(bool, default=False)
    }
    v = Validator(schema)

    # Valid
    data = {"host": "localhost", "port": 3000}
    assert v.validate(data) == {"host": "localhost", "port": 3000, "debug": False}

    # Missing required
    with pytest.raises(ValidationError, match="required"):
        v.validate({"port": 3000})

    # Wrong type (should cast for int/float/bool if possible, or fail)
    assert v.validate({"host": "localhost", "port": "9000"})["port"] == 9000

    with pytest.raises(ValidationError, match="type"):
        v.validate({"host": "localhost", "port": "abc"})

    # Range check
    with pytest.raises(ValidationError, match="less than minimum"):
        v.validate({"host": "localhost", "port": -1})

def test_schema_nested():
    db_schema = Validator({
        "host": SchemaField(str, required=True),
        "port": SchemaField(int, default=5432)
    })
    schema = {
        "database": db_schema,
        "app": SchemaField(str, default="myapp")
    }
    v = Validator(schema)

    # Valid
    data = {"database": {"host": "db.host"}}
    assert v.validate(data) == {
        "database": {"host": "db.host", "port": 5432},
        "app": "myapp"
    }

    # Missing nested required
    with pytest.raises(ValidationError, match="required"):
        v.validate({"database": {}})

def test_schema_choices():
    schema = {
        "env": SchemaField(str, choices=["dev", "prod", "test"])
    }
    v = Validator(schema)

    assert v.validate({"env": "dev"}) == {"env": "dev"}
    with pytest.raises(ValidationError, match="not one of"):
        v.validate({"env": "staging"})

def test_schema_unknown_keys():
    schema = {"a": SchemaField(int)}
    v = Validator(schema)
    assert v.validate({"a": 1, "b": 2}) == {"a": 1, "b": 2}

def test_schema_validation_error_nested():
    v = Validator({
        "nested": Validator({"a": SchemaField(int, required=True)})
    })
    with pytest.raises(ValidationError, match="must be a dictionary"):
        v.validate({"nested": "not a dict"})
