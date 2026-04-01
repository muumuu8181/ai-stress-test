import pytest
import os
from cirunner.conditions import evaluate_condition, should_run

def test_evaluate_condition_basic():
    vars = {'DEBUG': 'true'}
    env = {'STAGE': 'test'}

    assert evaluate_condition('${DEBUG}', vars, env) is True
    assert evaluate_condition('${env.STAGE} == "test"', vars, env) is True
    assert evaluate_condition('${env.STAGE} != "prod"', vars, env) is True
    assert evaluate_condition('${UNDEFINED}', vars, env) is False

def test_evaluate_condition_falsy():
    vars = {'FLAG': 'false', 'ZERO': '0', 'EMPTY': ''}
    assert evaluate_condition('${FLAG}', vars, {}) is False
    assert evaluate_condition('${ZERO}', vars, {}) is False
    assert evaluate_condition('${EMPTY}', vars, {}) is False

def test_should_run():
    vars = {'RUN_TESTS': 'true'}
    env = {'CI': 'true'}

    # if
    assert should_run('true', None, vars, env) is True
    assert should_run('false', None, vars, env) is False
    assert should_run('${RUN_TESTS}', None, vars, env) is True

    # unless
    assert should_run(None, 'false', vars, env) is True
    assert should_run(None, 'true', vars, env) is False
    assert should_run(None, '${env.CI}', vars, env) is False

    # both
    assert should_run('true', 'false', vars, env) is True
    assert should_run('false', 'false', vars, env) is False
    assert should_run('true', 'true', vars, env) is False
