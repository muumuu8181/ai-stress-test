import pytest
from qr_encoder.encoding import get_version_and_data_bits
from qr_encoder.constants import Mode, ErrorCorrectionLevel

def test_byte_mode_utf8_length_and_eci():
    data = "こんにちは" # 5 characters, 15 bytes in UTF-8
    version, mode, bits = get_version_and_data_bits(data, ErrorCorrectionLevel.L)
    # ECI bits (4) + ECI Assignment (8) + Mode bits (4) + Count bits (8 for V1 Byte) + Data bits (15 * 8 = 120)
    # ECI Assignment 26 = 00011010
    # Total = 4 + 8 + 4 + 8 + 120 = 144 bits.
    # Should start with ECI indicator 0111 and assignment 00011010
    assert bits.startswith("011100011010010000001111")
    assert len(bits) >= 144
