import pytest
from templateengine.engine import Environment, Template

def test_inheritance_simple():
    templates = {
        "base.html": "Header {% block content %}{% endblock %} Footer",
        "child.html": "{% extends \"base.html\" %}{% block content %}Body{% endblock %}"
    }
    env = Environment(loader=lambda name: templates.get(name))
    template = env.get_template("child.html")
    assert template.render() == "Header Body Footer"

def test_inheritance_multiple_blocks():
    templates = {
        "base.html": "{% block title %}Def{% endblock %} - {% block content %}{% endblock %}",
        "child.html": "{% extends \"base.html\" %}{% block title %}Child{% endblock %}{% block content %}Body{% endblock %}"
    }
    env = Environment(loader=lambda name: templates.get(name))
    template = env.get_template("child.html")
    assert template.render() == "Child - Body"

def test_inheritance_default_content():
    templates = {
        "base.html": "Header {% block content %}Default{% endblock %} Footer",
        "child.html": "{% extends \"base.html\" %}"
    }
    env = Environment(loader=lambda name: templates.get(name))
    template = env.get_template("child.html")
    assert template.render() == "Header Default Footer"

def test_inheritance_nested_blocks():
    templates = {
        "base.html": "A {% block main %}B {% block sub %}C{% endblock %} D{% endblock %} E",
        "child.html": "{% extends \"base.html\" %}{% block sub %}F{% endblock %}"
    }
    env = Environment(loader=lambda name: templates.get(name))
    template = env.get_template("child.html")
    assert template.render() == "A B F D E"

def test_inheritance_multi_level():
    templates = {
        "layout.html": "Layout [ {% block content %}{% endblock %} ]",
        "base.html": "{% extends \"layout.html\" %}{% block content %}Base ( {% block subcontent %}BaseDefault{% endblock %} ){% endblock %}",
        "child.html": "{% extends \"base.html\" %}{% block subcontent %}ChildOverride{% endblock %}"
    }
    env = Environment(loader=lambda name: templates.get(name))
    template = env.get_template("child.html")
    # Child overrides subcontent which is inside content of base.html.
    # When layout renders content, it calls base's content,
    # which calls subcontent (overridden by child).
    assert template.render() == "Layout [ Base ( ChildOverride ) ]"

def test_inheritance_multi_level_override():
    templates = {
        "layout.html": "L: {% block c %}Default{% endblock %}",
        "base.html": "{% extends \"layout.html\" %}{% block c %}B{% endblock %}",
        "child.html": "{% extends \"base.html\" %}{% block c %}C{% endblock %}"
    }
    env = Environment(loader=lambda name: templates.get(name))
    template = env.get_template("child.html")
    # Child should win over base.
    assert template.render() == "L: C"

def test_template_not_found():
    env = Environment(loader=lambda name: None)
    with pytest.raises(FileNotFoundError):
        env.get_template("nonexistent.html")
