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
