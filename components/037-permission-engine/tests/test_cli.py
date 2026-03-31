import io
from unittest.mock import patch
from permission_engine.cli import run_repl


def test_cli_integration():
    inputs = [
        "role user",
        "policy user file read",
        "role admin user",
        "policy admin file write",
        "check user file read",
        "check user file write",
        "check admin file read",
        "check admin file write",
        "exit"
    ]

    with patch("builtins.input", side_effect=inputs):
        with patch("sys.stdout", new=io.StringIO()) as mock_stdout:
            run_repl()
            output = mock_stdout.getvalue()

            assert "Role 'user' added." in output
            assert "Policy added for role 'user'." in output
            assert "Role 'admin' added." in output
            assert "Policy added for role 'admin'." in output

            # Check for ALLOWED/DENIED in output
            results = [line for line in output.splitlines() if line in ["ALLOWED", "DENIED"]]
            assert results == ["ALLOWED", "DENIED", "ALLOWED", "ALLOWED"]


def test_cli_missing_role():
    inputs = [
        "role admin nonexistent",
        "exit"
    ]

    with patch("builtins.input", side_effect=inputs):
        with patch("sys.stdout", new=io.StringIO()) as mock_stdout:
            run_repl()
            output = mock_stdout.getvalue()
            assert "Parent role 'nonexistent' not found." in output


def test_cli_unknown_command():
    inputs = [
        "unknown_cmd",
        "exit"
    ]

    with patch("builtins.input", side_effect=inputs):
        with patch("sys.stdout", new=io.StringIO()) as mock_stdout:
            run_repl()
            output = mock_stdout.getvalue()
            assert "Unknown command: unknown_cmd" in output


def test_cli_invalid_arguments():
    inputs = [
        "role",
        "policy",
        "check",
        "exit"
    ]

    with patch("builtins.input", side_effect=inputs):
        with patch("sys.stdout", new=io.StringIO()) as mock_stdout:
            run_repl()
            output = mock_stdout.getvalue()
            assert "Usage: role <name> [parent_name]" in output
            assert "Usage: policy <role_name> <resource> <action>" in output
            assert "Usage: check <role_name> <resource> <action>" in output
