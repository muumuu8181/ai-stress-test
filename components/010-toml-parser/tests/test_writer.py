import pytest
from tomlparser import dumps, loads

def test_dump_simple():
    data = {"key": "value", "number": 42}
    toml = dumps(data)
    assert 'key = "value"' in toml
    assert 'number = 42' in toml

def test_dump_tables():
    data = {
        "owner": {"name": "Tom"},
        "database": {"server": "localhost"}
    }
    toml = dumps(data)
    assert "[owner]\nname = \"Tom\"" in toml
    assert "[database]\nserver = \"localhost\"" in toml

def test_dump_roundtrip():
    data = {
        "title": "TOML Example",
        "owner": {"name": "Tom"},
        "database": {"server": "localhost", "ports": [8000, 8001]},
        "products": [{"name": "Hammer"}, {"name": "Nail"}]
    }
    toml = dumps(data)
    reloaded = loads(toml)
    assert reloaded == data

def test_dump_escapes():
    data = {"key": 'quote " test'}
    toml = dumps(data)
    assert 'key = "quote \\" test"' in toml
