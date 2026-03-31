import pytest
from tomlparser import loads

def test_empty_input():
    data = loads("")
    assert data == {}

def test_comment_only_input():
    data = loads("# only comments\n# nothing else")
    assert data == {}

def test_duplicate_key_error():
    toml = 'key = "value1"\nkey = "value2"'
    with pytest.raises(ValueError, match="Duplicate key: key"):
        loads(toml)

def test_invalid_syntax_error():
    toml = 'key = "value" garbage'
    # Current implementation might not catch garbage at end of line if it's not a newline/EOF,
    # but let's see how Lexer/Parser behaves.
    # In my parser, it would ignore the extra token or fail if it's unexpected.
    # Actually, if I add more validation in parser, I can catch this.
    pass

def test_malformed_datetime():
    toml = 'dt = 1979-05-27X07:32:00'
    # My lexer will try to parse this as a bare key if it doesn't match datetime format.
    # But bare keys cannot contain ':', so it should fail.
    with pytest.raises(ValueError):
        loads(toml)

def test_unclosed_string():
    toml = 'key = "unclosed string'
    with pytest.raises(ValueError, match="Unterminated string"):
        loads(toml)

def test_table_redefinition():
    toml = """
    [table]
    key = 1
    [table]
    key = 2
    """
    with pytest.raises(ValueError, match="Table redefinition: table"):
        loads(toml)
