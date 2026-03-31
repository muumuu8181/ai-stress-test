import os
import sys
import pytest
from taskrunner.cli import main
from taskrunner.parser import Parser
from unittest.mock import patch

def test_cli_list(capsys, tmp_path):
    os.chdir(tmp_path)
    f = tmp_path / "tasks.yaml"
    f.write_text("tasks:\n  t1:\n    cmds: [echo]")
    with patch.object(sys, 'argv', ['taskrunner', '-f', str(f), '-l']):
        main()
    captured = capsys.readouterr()
    assert "Available tasks:" in captured.out
    assert "t1" in captured.out

def test_cli_run(capsys, tmp_path):
    os.chdir(tmp_path)
    f = tmp_path / "tasks.yaml"
    f.write_text("tasks:\n  t1:\n    cmds: [echo hello]")
    with patch.object(sys, 'argv', ['taskrunner', '-f', str(f), 't1']):
        main()
    captured = capsys.readouterr()
    assert "Running 't1'" in captured.out
    assert "hello" in captured.out

def test_cli_file_not_found(capsys):
    with patch.object(sys, 'argv', ['taskrunner', '-f', 'nonexistent.yaml']):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1
    captured = capsys.readouterr()
    assert "not found" in captured.out

def test_cli_parse_error(capsys, tmp_path):
    f = tmp_path / "tasks.yaml"
    f.write_text("tasks:\n  t1:") # Valid but empty
    with patch.object(sys, 'argv', ['taskrunner', '-f', str(f)]):
        main()
    captured = capsys.readouterr()
    assert "Running 't1'" in captured.out

def test_cli_default_task(capsys, tmp_path):
    os.chdir(tmp_path)
    f = tmp_path / "tasks.yaml"
    f.write_text("tasks:\n  t1:\n    cmds: [echo default]")
    with patch.object(sys, 'argv', ['taskrunner', '-f', str(f)]):
        main()
    captured = capsys.readouterr()
    assert "Running 't1'" in captured.out
