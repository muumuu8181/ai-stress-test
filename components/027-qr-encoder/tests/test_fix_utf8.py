import pytest
from qr_encoder.encoding import get_version_and_data_bits
from qr_encoder.constants import Mode, ErrorCorrectionLevel

def test_byte_mode_utf8_length():
    data = "こんにちは" # 5 characters, 15 bytes in UTF-8
    version, mode, bits = get_version_and_data_bits(data, ErrorCorrectionLevel.L)
    # Mode bits (4) + Count bits (8 for V1 Byte) + Data bits (15 * 8 = 120)
    # Total = 4 + 8 + 120 = 132 bits.
    # Count should be 15 (00001111)
    assert bits.startswith("010000001111")
    assert len(bits) >= 132
