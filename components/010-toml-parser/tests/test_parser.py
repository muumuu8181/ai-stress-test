import pytest
from tomlparser import loads

def test_basic_key_value():
    toml = 'key = "value"\nnumber = 42\nbool = true'
    data = loads(toml)
    assert data['key'] == "value"
    assert data['number'] == 42
    assert data['bool'] is True

def test_dotted_keys():
    toml = 'physical.color = "orange"\nphysical.shape = "round"'
    data = loads(toml)
    assert data['physical']['color'] == "orange"
    assert data['physical']['shape'] == "round"

def test_tables():
    toml = """
    [table-1]
    key1 = "some string"
    key2 = 123

    [table-2]
    key1 = "another string"
    key2 = 456
    """
    data = loads(toml)
    assert data['table-1']['key1'] == "some string"
    assert data['table-1']['key2'] == 123
    assert data['table-2']['key1'] == "another string"
    assert data['table-2']['key2'] == 456

def test_array_of_tables():
    toml = """
    [[products]]
    name = "Hammer"
    sku = 738594937

    [[products]]
    name = "Nail"
    sku = 284758393
    """
    data = loads(toml)
    assert len(data['products']) == 2
    assert data['products'][0]['name'] == "Hammer"
    assert data['products'][1]['sku'] == 284758393

def test_inline_tables():
    toml = 'name = { first = "Tom", last = "Preston-Werner" }'
    data = loads(toml)
    assert data['name']['first'] == "Tom"
    assert data['name']['last'] == "Preston-Werner"

def test_arrays():
    toml = 'integers = [ 1, 2, 3 ]\ncolors = [ "red", "yellow", "green" ]'
    data = loads(toml)
    assert data['integers'] == [1, 2, 3]
    assert data['colors'] == ["red", "yellow", "green"]
