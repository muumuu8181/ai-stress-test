import hashlib
import hmac
from typing import BinaryIO


def calculate_hash(data: bytes, algorithm: str = "sha256") -> str:
    """Calculate the hash of the given bytes.

    Args:
        data: The bytes to hash.
        algorithm: The hashing algorithm to use (md5, sha1, sha256).

    Returns:
        The hex-encoded hash string.

    """
    h = hashlib.new(algorithm)
    h.update(data)
    return h.hexdigest()


def calculate_file_hash(
    file_obj: BinaryIO, algorithm: str = "sha256", chunk_size: int = 8192
) -> str:
    """Calculate the hash of a file-like object using streaming.

    Args:
        file_obj: The binary file-like object to hash.
        algorithm: The hashing algorithm to use (md5, sha1, sha256).
        chunk_size: The size of chunks to read from the file.

    Returns:
        The hex-encoded hash string.

    """
    h = hashlib.new(algorithm)
    while chunk := file_obj.read(chunk_size):
        h.update(chunk)
    return h.hexdigest()


def calculate_hmac(key: bytes, data: bytes, algorithm: str = "sha256") -> str:
    """Calculate the HMAC of the given data with the given key.

    Args:
        key: The secret key for HMAC.
        data: The data to hash.
        algorithm: The hashing algorithm to use (md5, sha1, sha256).

    Returns:
        The hex-encoded HMAC string.

    """
    # hashlib.new might be needed for the digestmod if algorithm name is used
    return hmac.new(key, data, digestmod=algorithm).hexdigest()
