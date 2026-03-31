import pytest
from qr_encoder import generate_qr, ErrorCorrectionLevel

def test_known_good_v1_l_numeric():
    # Known-good matrix for "123" at V1-L
    # Since masking can vary, we just check some key modules that are fixed.
    qr = generate_qr("123", ErrorCorrectionLevel.L)
    assert qr.size == 21
    # Finder patterns
    # Top left
    assert qr.matrix[0][0] is True
    assert qr.matrix[0][6] is True
    assert qr.matrix[6][0] is True
    assert qr.matrix[6][6] is True
    assert qr.matrix[3][3] is True
    # White separator
    assert qr.matrix[7][7] is False
    # Timing pattern
    assert qr.matrix[6][8] is True
    assert qr.matrix[6][9] is False
    assert qr.matrix[6][10] is True
    # Dark module
    assert qr.matrix[13][8] is True
