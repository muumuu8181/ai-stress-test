import pytest
from templateengine.engine import Environment, Template

def test_empty_template():
    env = Environment()
    template = Template("", env)
    assert template.render() == ""

def test_null_value():
    env = Environment()
    template = Template("Value: {{ val }}", env)
    # Our engine now correctly handles None
    assert template.render(val=None) == "Value: None"

def test_nested_attribute_error():
    env = Environment()
    template = Template("{{ user.nonexistent }}", env)
    with pytest.raises(NameError) as exc:
        template.render(user={"name": "Alice"})
    assert "Undefined attribute 'nonexistent'" in str(exc.value)

def test_invalid_filter_arg():
    env = Environment()
    template = Template("{{ items | join(\"|\") }}", env)
    assert template.render(items=["a", "b"]) == "a|b"

def test_large_template():
    env = Environment()
    content = "Hello " * 1000
    template = Template(content, env)
    assert template.render() == content

def test_complex_expression():
    env = Environment()
    # name | upper | safe
    template = Template("{{ name | upper | safe }}", env)
    assert template.render(name="<alice>") == "<ALICE>"
