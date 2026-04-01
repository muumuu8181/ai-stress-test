import pytest
import os
import tempfile
from cirunner.models import Pipeline
from cirunner.executor import Executor

def test_substitute_vars_non_string():
    pipeline_dict = {
        'vars': {'BUILD_NUM': 123},
        'stages': [
            {
                'name': 'test',
                'jobs': [
                    {'name': 'echo', 'run': 'echo ${BUILD_NUM}'}
                ]
            }
        ]
    }
    pipeline = Pipeline.from_dict(pipeline_dict)
    executor = Executor(pipeline)
    result = executor.run_pipeline()
    assert result.status == 'passed'
    assert '123' in result.stage_results[0].job_results[0].logs

def test_env_normalization_non_string():
    pipeline_dict = {
        'env': {'RETRIES': 3, 'DEBUG': True},
        'stages': [
            {
                'name': 'test',
                'jobs': [
                    {'name': 'env_check', 'run': 'echo $RETRIES $DEBUG'}
                ]
            }
        ]
    }
    pipeline = Pipeline.from_dict(pipeline_dict)
    executor = Executor(pipeline)
    result = executor.run_pipeline()
    assert result.status == 'passed'
    assert '3 True' in result.stage_results[0].job_results[0].logs

def test_artifact_globbing():
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, 'test1.txt')
        file2 = os.path.join(tmpdir, 'test2.txt')
        with open(file1, 'w') as f: f.write('1')
        with open(file2, 'w') as f: f.write('2')

        pipeline_dict = {
            'stages': [
                {
                    'name': 'test',
                    'jobs': [
                        {
                            'name': 'glob',
                            'run': 'true',
                            'artifacts': [os.path.join(tmpdir, '*.txt')]
                        }
                    ]
                }
            ]
        }
        pipeline = Pipeline.from_dict(pipeline_dict)
        executor = Executor(pipeline)
        result = executor.run_pipeline()

        artifacts = result.stage_results[0].job_results[0].artifacts_found
        assert len(artifacts) == 2
        assert file1 in artifacts
        assert file2 in artifacts
