import pytest
import os
import json
import tempfile
import subprocess
import sys

def test_full_pipeline_run():
    pipeline_yaml = """
vars:
  PROJECT: test_project
env:
  GLOBAL_ENV: global

stages:
  - name: test
    jobs:
      - name: unit_test
        run: echo "running tests for ${PROJECT}"
      - name: lint
        run: echo "linting"
  - name: build
    jobs:
      - name: compile
        run: echo "compiling ${GLOBAL_ENV}"
    """

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tf:
        tf.write(pipeline_yaml)
        tf_path = tf.name

    report_path = tf_path + ".report.json"

    try:
        # Run via CLI
        # Using sys.executable to run with current python
        # Need to set PYTHONPATH to include the components/050-ci-runner
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(os.getcwd(), 'components/050-ci-runner')

        result = subprocess.run(
            [sys.executable, '-m', 'cirunner', tf_path, '--report', report_path],
            env=env,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "Pipeline PASSED." in result.stdout

        # Check report
        assert os.path.exists(report_path)
        with open(report_path, 'r') as f:
            report = json.load(f)

        assert report['status'] == 'passed'
        assert len(report['stages']) == 2
        assert report['stages'][0]['name'] == 'test'
        assert len(report['stages'][0]['jobs']) == 2
        assert "running tests for test_project" in report['stages'][0]['jobs'][0]['logs']

    finally:
        if os.path.exists(tf_path):
            os.remove(tf_path)
        if os.path.exists(report_path):
            os.remove(report_path)

def test_failing_pipeline_cli():
    pipeline_yaml = """
stages:
  - name: fail_stage
    jobs:
      - run: exit 1
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tf:
        tf.write(pipeline_yaml)
        tf_path = tf.name

    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(os.getcwd(), 'components/050-ci-runner')

        result = subprocess.run(
            [sys.executable, '-m', 'cirunner', tf_path],
            env=env,
            capture_output=True,
            text=True
        )

        assert result.returncode != 0
        assert "Pipeline FAILED." in result.stdout
    finally:
        if os.path.exists(tf_path):
            os.remove(tf_path)
