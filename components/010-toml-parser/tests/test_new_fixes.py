import pytest
from tomlparser import loads, dumps

def test_numeric_keys():
    toml = '123 = "value"'
    data = loads(toml)
    assert data["123"] == "value"

def test_empty_list_serialization():
    data = {"arr": []}
    toml = dumps(data)
    assert 'arr = [  ]' in toml
    reloaded = loads(toml)
    assert reloaded == data

def test_leading_zeros_fail():
    toml = 'num = 01'
    with pytest.raises(ValueError, match="Invalid leading zero in integer"):
        loads(toml)

    toml2 = 'num = -01'
    with pytest.raises(ValueError, match="Invalid leading zero in integer"):
        loads(toml2)

def test_inline_table_trailing_comma_fail():
    toml = 't = { a = 1, }'
    with pytest.raises(ValueError, match="Trailing comma in inline table"):
        loads(toml)

def test_unexpected_top_level_token_fail():
    toml = 'key = "value" ,'
    with pytest.raises(ValueError, match="Unexpected token at top level"):
        loads(toml)
