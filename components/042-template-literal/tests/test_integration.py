import pytest
from templateliteral.engine import Environment, Template, TemplateSyntaxError

def test_render_variable():
    env = Environment()
    template = env.from_string("Hello, ${name}!")
    assert template.render(name="Alice") == "Hello, Alice!"

def test_render_expression():
    env = Environment()
    template = env.from_string("Sum: ${a + b}")
    assert template.render(a=1, b=2) == "Sum: 3"

def test_render_filters():
    env = Environment()
    template = env.from_string("Upper: ${name | upper}, Currency: ${price | currency}")
    assert template.render(name="alice", price=19.99) == "Upper: ALICE, Currency: $19.99"

def test_render_conditional():
    env = Environment()
    template = env.from_string("{?show}Yes{/?}{?not show}No{/?}")
    assert template.render(show=True) == "Yes"
    assert template.render(show=False) == "No"

def test_render_loop():
    env = Environment()
    template = env.from_string("{@each items as item}${item} {/each}")
    assert template.render(items=[1, 2, 3]) == "1 2 3 "

def test_render_nested_loop():
    env = Environment()
    template = env.from_string("{@each outer as o}{@each inner as i}${o}${i}{/each} {/each}")
    assert template.render(outer=["A"], inner=[1, 2]) == "A1A2 "

def test_render_html_escaping():
    env = Environment()
    template = env.from_string("${html}")
    # Python's html.escape also escapes single quotes by default in newer versions
    expected = "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
    assert template.render(html="<script>alert('xss')</script>") == expected

def test_render_safe_filter():
    env = Environment()
    template = env.from_string("${html | safe}")
    assert template.render(html="<b>Bold</b>") == "<b>Bold</b>"

def test_custom_filter():
    env = Environment()
    env.register_filter("bold", lambda x: f"<b>{x}</b>")
    template = env.from_string("${name | bold | safe}")
    assert template.render(name="World") == "<b>World</b>"

def test_error_line_number():
    env = Environment()
    # Syntax error
    with pytest.raises(TemplateSyntaxError) as excinfo:
        env.from_string("Line 1\nLine 2 {@each x} oops {/each}")
    assert "line 2" in str(excinfo.value)

def test_runtime_error_line_number():
    env = Environment()
    template = env.from_string("Line 1\nLine 2 ${undefined_var}")
    with pytest.raises(RuntimeError) as excinfo:
        template.render()
    assert "line 2" in str(excinfo.value)

def test_complex_expression():
    env = Environment()
    template = env.from_string("${user.name | upper}")
    class User:
        def __init__(self, name):
            self.name = name
    assert template.render(user=User("alice")) == "ALICE"

def test_each_item_access():
    env = Environment()
    template = env.from_string("{@each users as user}${user.id}: ${user.name | upper}{/each}")
    users = [{"id": 1, "name": "alice"}, {"id": 2, "name": "bob"}]
    # Note: dict access like user.id requires dot notation support in eval.
    # In Python, eval("user.id", {"user": {"id": 1}}) will fail.
    # We should probably use a safer way or support dict access if we want this to work.
    # Let's adjust the test to use objects for now, or use items like user['id'].
    class UserObj:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    users_obj = [UserObj(1, "alice"), UserObj(2, "bob")]
    assert template.render(users=users_obj) == "1: ALICE2: BOB"

def test_dict_dot_notation():
    env = Environment()
    template = env.from_string("${user.name}")
    assert template.render(user={"name": "Alice"}) == "Alice"

def test_empty_template():
    env = Environment()
    template = env.from_string("")
    assert template.render() == ""

def test_null_value():
    env = Environment()
    template = env.from_string("Value: ${val}")
    assert template.render(val=None) == "Value: None"
