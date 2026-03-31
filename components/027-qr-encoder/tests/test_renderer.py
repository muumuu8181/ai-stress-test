import pytest
from qr_encoder.renderer import to_ascii, to_pbm
from qr_encoder.matrix import QRMatrix

def test_to_ascii():
    m = QRMatrix(1)
    # Fill with something simple
    for r in range(m.size):
        for c in range(m.size):
            m.matrix[r][c] = (r + c) % 2 == 0

    ascii_out = to_ascii(m)
    assert "■" in ascii_out
    assert "□" in ascii_out
    # Size including quiet zone: 21 + 2*4 = 29
    lines = ascii_out.splitlines()
    assert len(lines) == 29
    assert len(lines[0]) == 29

def test_to_pbm():
    m = QRMatrix(1)
    for r in range(m.size):
        for c in range(m.size):
            m.matrix[r][c] = (r + c) % 2 == 0

    pbm_out = to_pbm(m)
    assert pbm_out.startswith("P1")
    assert "29 29" in pbm_out
    assert "1" in pbm_out
    assert "0" in pbm_out
