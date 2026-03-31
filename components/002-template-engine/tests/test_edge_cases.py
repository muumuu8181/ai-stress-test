import pytest
import os
from templateengine.engine import Environment, Template, FileSystemLoader

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

def test_chained_comparisons():
    env = Environment()
    assert Template("{% if 1 < 2 < 3 %}YES{% endif %}", env).render() == "YES"
    assert Template("{% if 1 < 5 < 3 %}YES{% else %}NO{% endif %}", env).render() == "NO"
    assert Template("{% if 10 > 5 > 1 %}YES{% endif %}", env).render() == "YES"

def test_comparison_in_strings():
    env = Environment()
    # Ensure operators inside strings don't break splitting
    assert Template("{% if val == '==' %}YES{% endif %}", env).render(val="==") == "YES"
    assert Template("{% if val != '!=' %}NO{% else %}YES{% endif %}", env).render(val="!=") == "YES"

def test_delimiters_in_strings():
    env = Environment()
    assert Template("{{ '}}' }}", env).render() == "}}"
    assert Template("{{ \"}}\" }}", env).render() == "}}"
    assert Template("{% if val == '}}' %}YES{% endif %}", env).render(val="}}") == "YES"

def test_path_traversal_protection(tmp_path):
    base = tmp_path / "templates"
    base.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("sensitive data")

    loader = FileSystemLoader(str(base))
    with pytest.raises(PermissionError):
        loader("../secret.txt")

def test_cyclic_inheritance():
    templates = {
        "A.html": "{% extends \"B.html\" %}",
        "B.html": "{% extends \"A.html\" %}"
    }
    env = Environment(loader=lambda name: templates.get(name))
    template = env.get_template("A.html")
    with pytest.raises(RuntimeError) as exc:
        template.render()
    assert "Cyclic inheritance detected" in str(exc.value)
