import os
import time
from taskrunner.core import Task

def test_task_expansion():
    task = Task(
        name="test",
        commands=["echo ${VAR}"],
        variables={"VAR": "local"}
    )
    task.expand_variables({"VAR": "global"})
    assert task.commands == ["echo local"]

    task = Task(
        name="test",
        commands=["echo ${VAR}"]
    )
    task.expand_variables({"VAR": "global"})
    assert task.commands == ["echo global"]

    os.environ["VAR"] = "env"
    task = Task(
        name="test",
        commands=["echo ${VAR}"]
    )
    task.expand_variables({})
    assert task.commands == ["echo env"]

def test_task_is_up_to_date(tmp_path):
    os.chdir(tmp_path)
    source = tmp_path / "source.txt"
    target = tmp_path / "target.txt"

    task = Task(name="test", sources=[str(source)], targets=[str(target)])

    # Target doesn't exist
    assert not task.is_up_to_date()

    # Target exists, source doesn't
    target.touch()
    assert not task.is_up_to_date()

    # Both exist, target newer
    source.touch()
    time.sleep(0.1)
    target.touch()
    assert task.is_up_to_date()

    # Source newer
    time.sleep(0.1)
    source.touch()
    assert not task.is_up_to_date()
