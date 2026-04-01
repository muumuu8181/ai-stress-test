import pytest
from cirunner.parser import parse_yaml

def test_parse_simple_yaml():
    yaml_str = """
key: value
number: 123
float: 1.23
boolean: true
null_val: null
    """
    result = parse_yaml(yaml_str)
    assert result['key'] == 'value'
    assert result['number'] == 123
    assert result['float'] == 1.23
    assert result['boolean'] is True
    assert result['null_val'] is None

def test_parse_nested_yaml():
    yaml_str = """
parent:
  child: value
  list:
    - item1
    - item2
    """
    result = parse_yaml(yaml_str)
    assert result['parent']['child'] == 'value'
    assert result['parent']['list'] == ['item1', 'item2']

def test_parse_list_of_dicts():
    yaml_str = """
stages:
  - name: stage1
    jobs:
      - run: cmd1
      - run: cmd2
  - name: stage2
    jobs:
      - run: cmd3
    """
    result = parse_yaml(yaml_str)
    assert len(result['stages']) == 2
    assert result['stages'][0]['name'] == 'stage1'
    assert len(result['stages'][0]['jobs']) == 2
    assert result['stages'][1]['jobs'][0]['run'] == 'cmd3'

def test_parse_comments_and_empty_lines():
    yaml_str = """
# This is a comment
key: value

  # Indented comment
nested:
  val: 1
    """
    result = parse_yaml(yaml_str)
    assert result['key'] == 'value'
    assert result['nested']['val'] == 1
