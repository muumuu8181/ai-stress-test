import pytest
import os
import time
import tempfile
from cirunner.models import Pipeline, Stage, Job
from cirunner.executor import Executor

def test_executor_simple_pipeline():
    pipeline_dict = {
        'stages': [
            {
                'name': 'test',
                'jobs': [
                    {'name': 'echo', 'run': 'echo "hello world"'},
                    {'name': 'true', 'run': 'true'}
                ]
            }
        ]
    }
    pipeline = Pipeline.from_dict(pipeline_dict)
    executor = Executor(pipeline)
    result = executor.run_pipeline()

    assert result.status == 'passed'
    assert len(result.stage_results) == 1
    assert result.stage_results[0].status == 'passed'
    assert len(result.stage_results[0].job_results) == 2
    assert 'hello world' in result.stage_results[0].job_results[0].logs

def test_executor_failing_job():
    pipeline_dict = {
        'stages': [
            {
                'name': 'fail_stage',
                'jobs': [
                    {'name': 'fail', 'run': 'exit 1'}
                ]
            },
            {
                'name': 'next_stage',
                'jobs': [
                    {'name': 'echo', 'run': 'echo "should not run"'}
                ]
            }
        ]
    }
    pipeline = Pipeline.from_dict(pipeline_dict)
    executor = Executor(pipeline)
    result = executor.run_pipeline()

    assert result.status == 'failed'
    assert len(result.stage_results) == 1 # Second stage should not run
    assert result.stage_results[0].status == 'failed'

def test_executor_allow_failure():
    pipeline_dict = {
        'stages': [
            {
                'name': 'fail_stage',
                'jobs': [
                    {'name': 'fail', 'run': 'exit 1', 'allow_failure': True},
                    {'name': 'success', 'run': 'true'}
                ]
            }
        ]
    }
    pipeline = Pipeline.from_dict(pipeline_dict)
    executor = Executor(pipeline)
    result = executor.run_pipeline()

    assert result.status == 'passed'
    assert result.stage_results[0].status == 'passed'
    # Find the job result for 'fail'
    fail_res = next(j for j in result.stage_results[0].job_results if j.job.name == 'fail')
    assert fail_res.status == 'failed'

def test_executor_timeout():
    pipeline_dict = {
        'stages': [
            {
                'name': 'timeout_stage',
                'jobs': [
                    {'name': 'slow', 'run': 'sleep 2', 'timeout': 1}
                ]
            }
        ]
    }
    pipeline = Pipeline.from_dict(pipeline_dict)
    executor = Executor(pipeline)
    result = executor.run_pipeline()

    assert result.status == 'failed'
    assert result.stage_results[0].job_results[0].status == 'timed_out'

def test_executor_artifacts():
    with tempfile.TemporaryDirectory() as tmpdir:
        art_path = os.path.join(tmpdir, 'artifact.txt')
        pipeline_dict = {
            'stages': [
                {
                    'name': 'build',
                    'jobs': [
                        {'name': 'create_art', 'run': f'echo "data" > {art_path}', 'artifacts': [art_path]}
                    ]
                }
            ]
        }
        pipeline = Pipeline.from_dict(pipeline_dict)
        executor = Executor(pipeline)
        result = executor.run_pipeline()

        assert result.status == 'passed'
        assert art_path in result.stage_results[0].job_results[0].artifacts_found

def test_executor_env_vars():
    pipeline_dict = {
        'env': {'PIPELINE_VAR': 'global_val'},
        'stages': [
            {
                'name': 'env_test',
                'jobs': [
                    {
                        'name': 'check_env',
                        'run': 'echo "${env.PIPELINE_VAR} ${env.JOB_VAR}"',
                        'env': {'JOB_VAR': 'job_val'}
                    }
                ]
            }
        ]
    }
    pipeline = Pipeline.from_dict(pipeline_dict)
    executor = Executor(pipeline)
    result = executor.run_pipeline()

    assert result.status == 'passed'
    logs = result.stage_results[0].job_results[0].logs
    assert 'global_val job_val' in logs
