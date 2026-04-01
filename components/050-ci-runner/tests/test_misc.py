import pytest
import os
import json
import tempfile
from cirunner.models import Pipeline, Stage, Job
from cirunner.executor import Executor
from cirunner.reporter import generate_report, save_report

def test_generate_report():
    pipeline_dict = {
        'stages': [
            {
                'name': 'test',
                'jobs': [
                    {'name': 'echo', 'run': 'echo "hello"'}
                ]
            }
        ]
    }
    pipeline = Pipeline.from_dict(pipeline_dict)
    executor = Executor(pipeline)
    result = executor.run_pipeline()

    report = generate_report(result)
    assert report['status'] == 'passed'
    assert report['stages'][0]['name'] == 'test'
    assert report['stages'][0]['jobs'][0]['name'] == 'echo'
    assert 'hello' in report['stages'][0]['jobs'][0]['logs']

def test_save_report():
    report = {"status": "passed"}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tf:
        tf_path = tf.name

    try:
        save_report(report, tf_path)
        with open(tf_path, 'r') as f:
            data = json.load(f)
        assert data['status'] == 'passed'
    finally:
        if os.path.exists(tf_path):
            os.remove(tf_path)

def test_executor_skipped_job():
    pipeline_dict = {
        'stages': [
            {
                'name': 'test',
                'jobs': [
                    {'name': 'skip_me', 'run': 'echo "skip"', 'if': 'false'}
                ]
            }
        ]
    }
    pipeline = Pipeline.from_dict(pipeline_dict)
    executor = Executor(pipeline)
    result = executor.run_pipeline()

    assert result.status == 'passed'
    assert result.stage_results[0].job_results[0].status == 'skipped'

def test_executor_artifact_not_found():
    pipeline_dict = {
        'stages': [
            {
                'name': 'test',
                'jobs': [
                    {'name': 'no_art', 'run': 'true', 'artifacts': ['non_existent.txt']}
                ]
            }
        ]
    }
    pipeline = Pipeline.from_dict(pipeline_dict)
    executor = Executor(pipeline)
    result = executor.run_pipeline()

    assert result.status == 'passed'
    assert 'Warning: Artifact not found' in result.stage_results[0].job_results[0].logs

def test_models_edge_cases():
    # Empty stages
    p = Pipeline.from_dict({})
    assert p.stages == []

    # Invalid job data
    s = Stage.from_dict({'name': 's', 'jobs': [123, None]})
    assert s.jobs == []

    # Job from dict with missing run
    j = Job.from_dict({}, 'default')
    assert j.name == 'default'
    assert j.run == ''
