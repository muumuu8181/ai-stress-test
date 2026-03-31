import codecs


def rot13(data: str) -> str:
    """Apply ROT13 transformation to a string.

    Args:
        data: The input string.

    Returns:
        The ROT13-transformed string.

    """
    return codecs.encode(data, "rot_13")
