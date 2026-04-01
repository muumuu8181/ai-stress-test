import pytest
from cirunner.parser import parse_yaml
from cirunner.conditions import should_run

def test_parser_colon_in_list_item():
    yaml_str = """
jobs:
  - echo http://example.com
  - name: job_with_colon
    run: "cmd: val"
    """
    result = parse_yaml(yaml_str)
    assert result['jobs'][0] == "echo http://example.com"
    assert isinstance(result['jobs'][1], dict)
    assert result['jobs'][1]['name'] == "job_with_colon"

def test_should_run_boolean():
    vars = {}
    env = {}

    # if: false (as boolean)
    assert should_run(False, None, vars, env) is False
    # if: true (as boolean)
    assert should_run(True, None, vars, env) is True

    # unless: true (as boolean)
    assert should_run(None, True, vars, env) is False
    # unless: false (as boolean)
    assert should_run(None, False, vars, env) is True

def test_condition_substitution_non_string():
    vars = {'BUILD_NUM': 123}
    env = {'DEBUG': True}

    # should not crash and should evaluate correctly
    assert should_run('${BUILD_NUM} == 123', None, vars, env) is True
    assert should_run('${env.DEBUG}', None, vars, env) is True
