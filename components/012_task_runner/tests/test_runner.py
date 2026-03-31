import pytest
import os
import subprocess
from taskrunner.core import Runner, Task

def test_runner_error_handling(capsys):
    t1 = Task("t1", commands=["exit 1"])
    runner = Runner([t1])
    assert not runner.run(["t1"])
    captured = capsys.readouterr()
    assert "failed with return code 1" in captured.out

def test_runner_parallel_error(tmp_path):
    os.chdir(tmp_path)
    t1 = Task("t1", commands=["exit 1"])
    t2 = Task("t2", dependencies=["t1"], commands=["touch t2_done"])
    runner = Runner([t1, t2], parallel=2)
    assert not runner.run(["t2"])
    assert not os.path.exists("t2_done")

def test_runner_missing_task_in_run(capsys):
    runner = Runner([])
    assert not runner.run(["nonexistent"])
    captured = capsys.readouterr()
    assert "Task 'nonexistent' not found" in captured.err

def test_runner_no_tasks(capsys):
    runner = Runner([])
    assert runner.run([])
    captured = capsys.readouterr()
    assert "No tasks to run" in captured.out

def test_task_expansion_missing_var():
    task = Task("t", commands=["echo ${MISSING}"])
    task.expand_variables({})
    assert task.commands == ["echo ${MISSING}"]
