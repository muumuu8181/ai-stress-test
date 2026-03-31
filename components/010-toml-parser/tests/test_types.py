import pytest
import datetime
from tomlparser import loads

def test_integers():
    toml = 'int1 = +99\nint2 = 42\nint3 = 0\nint4 = -17\nint5 = 1_000'
    data = loads(toml)
    assert data['int1'] == 99
    assert data['int2'] == 42
    assert data['int3'] == 0
    assert data['int4'] == -17
    assert data['int5'] == 1000

def test_floats():
    toml = 'flt1 = +1.0\nflt2 = 3.1415\nflt3 = -0.01\nflt4 = 5e+22\nflt5 = 1e06\nflt6 = -2E-2'
    data = loads(toml)
    assert data['flt1'] == 1.0
    assert data['flt2'] == 3.1415
    assert data['flt3'] == -0.01
    assert data['flt4'] == 5e+22
    assert data['flt5'] == 1e06
    assert data['flt6'] == -0.02

def test_booleans():
    toml = 'bool1 = true\nbool2 = false'
    data = loads(toml)
    assert data['bool1'] is True
    assert data['bool2'] is False

def test_datetimes():
    toml = """
    odt1 = 1979-05-27T07:32:00Z
    ldt1 = 1979-05-27T07:32:00
    ld1 = 1979-05-27
    lt1 = 07:32:00
    """
    data = loads(toml)
    assert isinstance(data['odt1'], datetime.datetime)
    assert data['odt1'].tzinfo == datetime.timezone.utc
    assert isinstance(data['ldt1'], datetime.datetime)
    assert data['ldt1'].tzinfo is None
    assert isinstance(data['ld1'], datetime.date)
    assert isinstance(data['lt1'], datetime.time)

def test_strings():
    toml = """
    str1 = "basic string"
    str2 = \"\"\"multi-line
string\"\"\"
    str3 = 'literal string'
    str4 = '''multi-line
literal string'''
    str5 = "string with \\"quote\\""
    str6 = \"\"\"multi-line with \\"\\"\\"quotes\\"\\"\\"\"\"\"
    """
    data = loads(toml)
    assert data['str1'] == "basic string"
    assert data['str2'] == "multi-line\nstring"
    assert data['str3'] == "literal string"
    assert data['str4'] == "multi-line\nliteral string"
    assert data['str5'] == 'string with "quote"'
    assert data['str6'] == 'multi-line with """quotes"""'

def test_inf_nan():
    toml = """
    f1 = inf
    f2 = +inf
    f3 = -inf
    f4 = nan
    f5 = +nan
    f6 = -nan
    """
    data = loads(toml)
    assert data['f1'] == float('inf')
    assert data['f2'] == float('inf')
    assert data['f3'] == float('-inf')
    import math
    assert math.isnan(data['f4'])
    assert math.isnan(data['f5'])
    assert math.isnan(data['f6'])
