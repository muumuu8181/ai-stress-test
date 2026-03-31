import os
from taskrunner.parser import Parser, parse_file

def test_parser_basic():
    content = """
vars:
  PROJECT: test
tasks:
  build:
    cmds: [echo ${PROJECT}]
"""
    parser = Parser(content)
    result = parser.parse()
    assert result["vars"]["PROJECT"] == "test"
    assert result["tasks"]["build"]["cmds"] == ["echo ${PROJECT}"]

def test_parser_indentation():
    content = """
tasks:
  build:
    cmds:
      - echo test
      - echo build
    deps:
      - prepare
  prepare:
    cmds:
      - mkdir build
"""
    parser = Parser(content)
    result = parser.parse()
    assert result["tasks"]["build"]["cmds"] == ["echo test", "echo build"]
    assert result["tasks"]["build"]["deps"] == ["prepare"]
    assert result["tasks"]["prepare"]["cmds"] == ["mkdir build"]

def test_parse_file(tmp_path):
    f = tmp_path / "tasks.yaml"
    f.write_text("""
vars:
  GVAR: g
tasks:
  t:
    cmds: [echo ${GVAR}]
""")
    tasks = parse_file(str(f))
    assert len(tasks) == 1
    assert tasks[0].name == "t"
    assert tasks[0].commands == ["echo g"]

def test_parser_empty_sections():
    content = """
vars:
tasks:
  t1:
    cmds: [echo]
"""
    parser = Parser(content)
    result = parser.parse()
    assert result["vars"] == {}
    assert "t1" in result["tasks"]

def test_parser_scalar_to_list():
    content = """
tasks:
  t1:
    cmds: echo hello
    deps: t2
  t2:
    cmds: echo world
"""
    parser = Parser(content)
    result = parser.parse()
    assert result["tasks"]["t1"]["cmds"] == "echo hello"
    assert result["tasks"]["t1"]["deps"] == "t2"

    # Check if parse_file normalizes them
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(content)
        f_path = f.name
    try:
        tasks = parse_file(f_path)
        t1 = next(t for t in tasks if t.name == "t1")
        assert t1.commands == ["echo hello"]
        assert t1.dependencies == ["t2"]
    finally:
        os.remove(f_path)
