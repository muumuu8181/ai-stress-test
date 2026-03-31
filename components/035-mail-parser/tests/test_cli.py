import pytest
from unittest.mock import patch, MagicMock
from cli import main
import sys
import os
import json
import io

def test_cli_basic(tmp_path):
    email_content = "Subject: Test\r\n\r\nBody"
    email_file = tmp_path / "test.eml"
    email_file.write_text(email_content)

    output_file = tmp_path / "output.json"

    test_args = ["cli.py", str(email_file), "-o", str(output_file)]
    with patch.object(sys, 'argv', test_args):
        main()

    assert output_file.exists()
    with open(output_file, 'r') as f:
        data = json.load(f)
    assert data["subject"] == "Test"
    assert data["content"]["text"] == "Body"

def test_cli_attachments(tmp_path):
    raw_email = (
        "Subject: Attachments\r\n"
        "Content-Type: multipart/mixed; boundary=boundary\r\n\r\n"
        "--boundary\r\n"
        "Content-Type: text/plain\r\n\r\n"
        "Body\r\n"
        "--boundary\r\n"
        "Content-Type: application/octet-stream\r\n"
        "Content-Disposition: attachment; filename=\"test.txt\"\r\n\r\n"
        "Hello World\r\n"
        "--boundary--"
    )
    email_file = tmp_path / "test.eml"
    email_file.write_bytes(raw_email.encode('utf-8'))

    att_dir = tmp_path / "attachments"

    test_args = ["cli.py", str(email_file), "-a", str(att_dir)]
    with patch.object(sys, 'argv', test_args):
        # Suppress stdout
        with patch('sys.stdout', new=io.StringIO()):
            main()

    assert (att_dir / "test.txt").exists()
    assert (att_dir / "test.txt").read_text() == "Hello World"

def test_cli_attachment_collisions(tmp_path):
    raw_email = (
        "Subject: Collision Test\r\n"
        "Content-Type: multipart/mixed; boundary=boundary\r\n\r\n"
        "--boundary\r\n"
        "Content-Type: application/octet-stream\r\n"
        "Content-Disposition: attachment; filename=\"test.txt\"\r\n\r\n"
        "First file\r\n"
        "--boundary\r\n"
        "Content-Type: application/octet-stream\r\n"
        "Content-Disposition: attachment; filename=\"test.txt\"\r\n\r\n"
        "Second file\r\n"
        "--boundary--"
    )
    email_file = tmp_path / "test.eml"
    email_file.write_bytes(raw_email.encode('utf-8'))

    att_dir = tmp_path / "attachments"

    test_args = ["cli.py", str(email_file), "-a", str(att_dir)]
    with patch.object(sys, 'argv', test_args):
        with patch('sys.stdout', new=io.StringIO()):
            main()

    assert (att_dir / "test.txt").exists()
    assert (att_dir / "test_1.txt").exists()
    assert (att_dir / "test.txt").read_text() == "First file"
    assert (att_dir / "test_1.txt").read_text() == "Second file"

def test_cli_stdin(tmp_path):
    email_content = b"Subject: Stdin Test\r\n\r\nBody"

    test_args = ["cli.py", "-"]
    with patch.object(sys, 'argv', test_args):
        mock_stdin = MagicMock()
        mock_stdin.buffer.read.return_value = email_content
        with patch('sys.stdin', mock_stdin):
            with patch('sys.stdout', new=io.StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()
                data = json.loads(output)
                assert data["subject"] == "Stdin Test"

def test_cli_error():
    test_args = ["cli.py", "nonexistent.eml"]
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit) as cm:
            main()
        assert cm.value.code == 1
