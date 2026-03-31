import pytest
import datetime
from tomlparser import loads, dumps

def test_p1_plain_table_on_aot_path():
    toml = """
    [[products]]
    name = "Hammer"
    [products]
    name = "Nail"
    """
    with pytest.raises(ValueError, match="already exists and is not a standard table"):
        loads(toml)

def test_p1_array_commas():
    # Correct
    loads("arr = [1, 2]")
    # Incorrect
    with pytest.raises(ValueError, match="Expected comma or ']'"):
        loads("arr = [1 2]")

def test_p1_base_prefixed_integers():
    data = loads("n1 = 0xDEADBEEF\nn2 = 0o755\nn3 = 0b1101")
    assert data["n1"] == 0xDEADBEEF
    assert data["n2"] == 0o755
    assert data["n3"] == 0b1101

def test_p1_float_syntax_validation():
    # Invalid: trailing dot
    with pytest.raises(ValueError):
        loads("f = 1.")
    # Invalid: leading dot
    with pytest.raises(ValueError):
        loads("f = .1")
    # Invalid: leading zero in integer part
    with pytest.raises(ValueError, match="Leading zeros are not allowed"):
        loads("f = 01.2")

def test_p2_underscore_placement():
    # Valid
    loads("n = 1_000")
    # Invalid: start
    with pytest.raises(ValueError, match="Underscore cannot be at the start"):
        loads("n = _123")
    # Invalid: end
    with pytest.raises(ValueError, match="Underscore cannot be at the start or end"):
        loads("n = 123_")
    # Invalid: consecutive
    with pytest.raises(ValueError, match="Consecutive underscores"):
        loads("n = 1__23")
    # Invalid: next to dot
    with pytest.raises(ValueError, match="Underscore must be between digits"):
        loads("f = 1_.2")
    with pytest.raises(ValueError, match="Underscore must be between digits"):
        loads("f = 1._2")

def test_p2_dotted_key_redefinition():
    toml = """
    a.b = 1
    [a]
    c = 2
    """
    with pytest.raises(ValueError, match="Table redefinition: a"):
        loads(toml)

def test_p2_high_precision_datetime():
    # 9 fractional digits
    toml = "dt = 1979-05-27T07:32:00.123456789Z"
    data = loads(toml)
    assert data["dt"].microsecond == 123456

def test_p2_underscores_in_floats():
    data = loads("f = 1_2.3_4")
    assert data["f"] == 12.34
