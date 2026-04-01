import pytest
from templateliteral.engine import Environment, TemplateSyntaxError

def test_pipes_in_strings():
    env = Environment()
    # Pipe inside a string literal should NOT be treated as a filter separator
    template = env.from_string("${'a|b' | upper}")
    assert template.render() == "A|B"

def test_security_access_blocked():
    env = Environment()
    # Test blocked access to dangerous attributes
    dangerous_templates = [
        "${''.__class__}",
        "${user._private}",
        "${[].__class__.__base__}",
    ]
    class User:
        def __init__(self):
            self._private = "secret"

    for src in dangerous_templates:
        template = env.from_string(src)
        with pytest.raises(RuntimeError) as excinfo:
            template.render(user=User())
        assert "Access to private attribute" in str(excinfo.value) or "Unsupported expression node" in str(excinfo.value)

def test_arithmetic_logic():
    env = Environment()
    template = env.from_string("${(a + b) * c > 10 and 'Yes' or 'No'}")
    assert template.render(a=1, b=2, c=5) == "Yes"
    assert template.render(a=1, b=1, c=2) == "No"

def test_list_dict_literals():
    env = Environment()
    template = env.from_string("${ [1, 2, 3][0] }")
    assert template.render() == "1"
    template = env.from_string("${ {'a': 1}['a'] }")
    assert template.render() == "1"

def test_in_operator():
    env = Environment()
    template = env.from_string("${ 'a' in items }")
    assert template.render(items=['a', 'b']) == "True"
    assert template.render(items=['c', 'd']) == "False"
