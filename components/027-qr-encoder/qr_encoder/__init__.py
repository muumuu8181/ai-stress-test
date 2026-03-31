from typing import Optional
from .constants import ErrorCorrectionLevel
from .encoding import get_version_and_data_bits, bits_to_codewords, interleave_blocks
from .matrix import QRMatrix, generate_optimal_matrix
from .renderer import to_ascii, to_pbm

__all__ = ["ErrorCorrectionLevel", "generate_qr", "to_ascii", "to_pbm", "QRMatrix"]

def generate_qr(data: str, ec_level: ErrorCorrectionLevel = ErrorCorrectionLevel.M) -> QRMatrix:
    """
    Generates a QR code for the given data and error correction level.

    Args:
        data: The string to encode.
        ec_level: The error correction level (L, M, Q, H).

    Returns:
        A QRMatrix object.
    """
    version, mode, bitstream = get_version_and_data_bits(data, ec_level)
    data_codewords = bits_to_codewords(bitstream)
    final_codewords = interleave_blocks(version, ec_level, data_codewords)

    matrix = generate_optimal_matrix(version, ec_level, final_codewords)
    return matrix
