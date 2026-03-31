import hashlib
import io

from enctool.hash_tool import calculate_file_hash, calculate_hash, calculate_hmac


def test_calculate_hash():
    data = b"hello"
    assert calculate_hash(data, "md5") == hashlib.md5(data).hexdigest()
    assert calculate_hash(data, "sha1") == hashlib.sha1(data).hexdigest()
    assert calculate_hash(data, "sha256") == hashlib.sha256(data).hexdigest()


def test_calculate_file_hash():
    data = b"hello world" * 1000
    file_obj = io.BytesIO(data)
    assert calculate_file_hash(file_obj, "sha256") == hashlib.sha256(data).hexdigest()


def test_calculate_hmac():
    key = b"secret"
    data = b"hello"
    import hmac

    expected = hmac.new(key, data, hashlib.sha256).hexdigest()
    assert calculate_hmac(key, data, "sha256") == expected


def test_hash_empty():
    assert calculate_hash(b"", "sha256") == hashlib.sha256(b"").hexdigest()
