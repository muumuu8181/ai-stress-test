import pytest
from templateengine.engine import Environment, Template

def test_empty_template():
    env = Environment()
    template = Template("", env)
    assert template.render() == ""

def test_null_value():
    env = Environment()
    template = Template("Value: {{ val }}", env)
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

def test_boolean_logic():
    env = Environment()
    assert Template("{% if True and True %}YES{% endif %}", env).render() == "YES"
    assert Template("{% if True and False %}YES{% else %}NO{% endif %}", env).render() == "NO"
    assert Template("{% if False or True %}YES{% endif %}", env).render() == "YES"
    assert Template("{% if not False %}YES{% endif %}", env).render() == "YES"
    assert Template("{% if 10 > 5 and 5 < 10 %}YES{% endif %}", env).render() == "YES"

def test_comparison_in_strings():
    env = Environment()
    # Ensure operators inside strings don't break splitting
    assert Template("{% if val == '==' %}YES{% endif %}", env).render(val="==") == "YES"
    assert Template("{% if val != '!=' %}NO{% else %}YES{% endif %}", env).render(val="!=") == "YES"
