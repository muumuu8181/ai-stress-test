import zlib


def calculate_crc32(data: bytes) -> str:
    """Calculate the CRC32 checksum of the given bytes.

    Args:
        data: The bytes to calculate CRC32 for.

    Returns:
        The hex-encoded CRC32 checksum string.

    """
    crc = zlib.crc32(data)
    # Convert to unsigned 32-bit integer hex string
    return f"{crc & 0xFFFFFFFF:08x}"
