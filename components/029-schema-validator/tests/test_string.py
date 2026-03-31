import pytest
from schemavalidator import validate, ValidationError

def test_string_minLength():
    schema = {"type": "string", "minLength": 3}
    validate("abc", schema)
    with pytest.raises(ValidationError):
        validate("ab", schema)

def test_string_maxLength():
    schema = {"type": "string", "maxLength": 5}
    validate("abcde", schema)
    with pytest.raises(ValidationError):
        validate("abcdef", schema)

def test_string_pattern():
    schema = {"type": "string", "pattern": "^[0-9]{3}-[0-9]{4}$"}
    validate("123-4567", schema)
    with pytest.raises(ValidationError):
        validate("123-456", schema)
    with pytest.raises(ValidationError):
        validate("abc-defg", schema)

def test_string_format_email():
    schema = {"type": "string", "format": "email"}
    validate("user@example.com", schema)
    with pytest.raises(ValidationError):
        validate("invalid-email", schema)

def test_string_format_uri():
    schema = {"type": "string", "format": "uri"}
    validate("https://example.com/path?q=1#frag", schema)
    validate("ftp://user:pass@host:21/file", schema)
    with pytest.raises(ValidationError):
        validate("not-a-uri", schema)

def test_string_format_date():
    schema = {"type": "string", "format": "date"}
    validate("2023-12-31", schema)
    with pytest.raises(ValidationError):
        validate("31-12-2023", schema)
    with pytest.raises(ValidationError):
        validate("2023-13-01", schema)

def test_string_keywords_non_string():
    # Keywords should be ignored if the type is not a string
    schema = {"type": "number", "minLength": 3}
    validate(12, schema)
