import pytest
from templateengine.engine import Environment, Template, FileSystemLoader
from templateengine.filters import SafeString

def test_engine_render_simple():
    env = Environment()
    template = Template("Hello, {{ name }}!", env)
    result = template.render(name="World")
    assert result == "Hello, World!"

def test_engine_render_if():
    env = Environment()
    template = Template("{% if user %}Hello, {{ user.name }}!{% else %}Guest{% endif %}", env)
    assert template.render(user={"name": "Alice"}) == "Hello, Alice!"
    assert template.render(user=None) == "Guest"

def test_engine_render_for():
    env = Environment()
    template = Template("{% for item in items %}{{ item }} {% endfor %}", env)
    assert template.render(items=[1, 2, 3]) == "1 2 3 "

def test_engine_autoescape():
    env = Environment(autoescape=True)
    template = Template("{{ script }}", env)
    assert template.render(script="<script>") == "&lt;script&gt;"

    template_safe = Template("{{ script | safe }}", env)
    assert template_safe.render(script="<script>") == "<script>"

def test_engine_expression_literals():
    env = Environment()
    template = Template("{{ 'hello' }} {{ 123 }} {{ True }}", env)
    assert template.render() == "hello 123 True"

def test_engine_nested_attribute():
    env = Environment()
    class User:
        def __init__(self, name):
            self.name = name
    template = Template("{{ user.name }}", env)
    assert template.render(user=User("Bob")) == "Bob"

def test_engine_undefined_variable():
    env = Environment()
    template = Template("{{ unknown }}", env)
    with pytest.raises(NameError) as exc:
        template.render()
    assert "Undefined variable 'unknown'" in str(exc.value)
    assert "line 1" in str(exc.value)
