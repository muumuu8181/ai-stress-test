import pytest
from qr_encoder.matrix import QRMatrix, generate_optimal_matrix
from qr_encoder.constants import ErrorCorrectionLevel

def test_qr_matrix_init():
    m = QRMatrix(1)
    assert m.size == 21
    assert len(m.matrix) == 21
    assert m.matrix[0][0] is None

def test_place_finder_patterns():
    m = QRMatrix(1)
    m.place_finder_patterns()
    # Top-left finder pattern
    assert m.matrix[0][0] is True
    assert m.matrix[1][1] is False
    assert m.matrix[2][2] is True
    assert m.reserved[0][0] is True

def test_place_timing_patterns():
    m = QRMatrix(1)
    m.place_timing_patterns()
    assert m.matrix[6][8] is True
    assert m.matrix[6][9] is False
    assert m.matrix[8][6] is True
    assert m.matrix[9][6] is False

def test_generate_optimal_matrix():
    # Small data
    codewords = [64, 85, 108, 108, 15, 17, 236, 17, 236, 17, 236, 17, 236, 17, 236, 17]
    # Interleave some EC
    full_codewords = codewords + [0] * 10
    m = generate_optimal_matrix(1, ErrorCorrectionLevel.M, full_codewords)
    assert m.size == 21
    # Check that it's mostly filled
    none_count = sum(row.count(None) for row in m.matrix)
    assert none_count == 0
