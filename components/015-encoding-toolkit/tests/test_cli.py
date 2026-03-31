import hashlib
import hmac
import os
import tempfile
import zlib

from enctool.cli import main


def test_cli_base64(capsys):
    main(["base64", "encode", "hello"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "aGVsbG8="

    main(["base64", "decode", "aGVsbG8=", "--text"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "hello"


def test_cli_base64_binary(capsys):
    # Test binary output (default)
    # Redirecting to a buffer in test might be tricky with capsys.
    # But we can at least check it doesn't crash for non-UTF8.
    # P_79 decodes to b"\x3f\xfe\xfd" or similar?
    # Actually __79 is b"\xff\xfe\xfd"
    with capsys.disabled():
        main(["base64", "decode", "P_79", "--url-safe"])


def test_cli_url(capsys):
    main(["url", "encode", "hello world"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "hello%20world"

    main(["url", "decode", "hello%20world"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "hello world"


def test_cli_hash(capsys):
    main(["hash", "md5", "hello"])
    captured = capsys.readouterr()
    assert captured.out.strip() == hashlib.md5(b"hello").hexdigest()


def test_cli_hash_file(capsys):
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"hello world")
        fname = f.name
    try:
        main(["hash", "sha256", fname, "--file"])
        captured = capsys.readouterr()
        assert captured.out.strip() == hashlib.sha256(b"hello world").hexdigest()
    finally:
        os.remove(fname)


def test_cli_hmac(capsys):
    main(["hmac", "sha256", "key", "hello"])
    captured = capsys.readouterr()
    expected = hmac.new(b"key", b"hello", hashlib.sha256).hexdigest()
    assert captured.out.strip() == expected


def test_cli_crc32(capsys):
    main(["crc32", "hello"])
    captured = capsys.readouterr()
    expected = f"{zlib.crc32(b'hello') & 0xFFFFFFFF:08x}"
    assert captured.out.strip() == expected


def test_cli_rot13(capsys):
    main(["rot13", "hello"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "uryyb"


def test_cli_detect(capsys):
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write("こんにちは".encode("shift-jis"))
        fname = f.name
    try:
        main(["detect", fname])
        captured = capsys.readouterr()
        assert captured.out.strip() == "shift-jis"
    finally:
        os.remove(fname)


def test_cli_convert(capsys):
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write("こんにちは".encode("utf-8"))
        fname = f.name
    try:
        # Using capsys.disabled() to avoid capturing binary output that causes UnicodeDecodeError in pytest's capture
        with capsys.disabled():
            main(["convert", fname, "--from-enc", "utf-8", "--to-enc", "shift-jis"])
    finally:
        os.remove(fname)


def test_cli_hex(capsys):
    main(["hex", "encode", "hello"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "68656c6c6f"

    main(["hex", "decode", "68656c6c6f", "--text"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "hello"
