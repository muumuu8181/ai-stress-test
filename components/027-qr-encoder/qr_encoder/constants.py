from enum import IntEnum
from typing import Dict, List, NamedTuple, Tuple

class ErrorCorrectionLevel(IntEnum):
    L = 1  # 7%
    M = 0  # 15%
    Q = 3  # 25%
    H = 2  # 30%

class Mode(IntEnum):
    NUMERIC = 0x1
    ALPHANUMERIC = 0x2
    BYTE = 0x4
    KANJI = 0x8  # Not required but good to have defined
    ECI = 0x7

# Version-specific information
class VersionInfo(NamedTuple):
    version: int
    total_codewords: int
    # ec_level -> (num_ec_codewords_per_block, List[num_blocks])
    # num_blocks is a list because some versions have blocks of slightly different sizes
    ec_blocks: Dict[ErrorCorrectionLevel, Tuple[int, List[Tuple[int, int]]]]

# Alignment pattern locations for versions 1-10
ALIGNMENT_PATTERNS: Dict[int, List[int]] = {
    1: [],
    2: [6, 18],
    3: [6, 22],
    4: [6, 26],
    5: [6, 30],
    6: [6, 34],
    7: [6, 22, 38],
    8: [6, 24, 42],
    9: [6, 26, 46],
    10: [6, 28, 50],
}

# (Version, EC Level) -> (Total data capacity in bits)
# This is a simplified view, actual capacity depends on mode
# For now, let's store the EC configuration for versions 1-10
# Format: (num_ec_codewords_per_block, [(num_blocks, data_codewords_per_block), ...])
EC_CONFIG: Dict[int, Dict[ErrorCorrectionLevel, Tuple[int, List[Tuple[int, int]]]]] = {
    1: {
        ErrorCorrectionLevel.L: (7, [(1, 19)]),
        ErrorCorrectionLevel.M: (10, [(1, 16)]),
        ErrorCorrectionLevel.Q: (13, [(1, 13)]),
        ErrorCorrectionLevel.H: (17, [(1, 9)]),
    },
    2: {
        ErrorCorrectionLevel.L: (10, [(1, 34)]),
        ErrorCorrectionLevel.M: (16, [(1, 28)]),
        ErrorCorrectionLevel.Q: (22, [(1, 22)]),
        ErrorCorrectionLevel.H: (28, [(1, 16)]),
    },
    3: {
        ErrorCorrectionLevel.L: (15, [(1, 55)]),
        ErrorCorrectionLevel.M: (26, [(1, 44)]),
        ErrorCorrectionLevel.Q: (18, [(2, 17)]),
        ErrorCorrectionLevel.H: (22, [(2, 13)]),
    },
    4: {
        ErrorCorrectionLevel.L: (20, [(1, 80)]),
        ErrorCorrectionLevel.M: (18, [(2, 32)]),
        ErrorCorrectionLevel.Q: (26, [(2, 24)]),
        ErrorCorrectionLevel.H: (16, [(4, 9)]),
    },
    5: {
        ErrorCorrectionLevel.L: (26, [(1, 108)]),
        ErrorCorrectionLevel.M: (24, [(2, 43)]),
        ErrorCorrectionLevel.Q: (18, [(2, 15), (2, 16)]),
        ErrorCorrectionLevel.H: (22, [(2, 11), (2, 12)]),
    },
    6: {
        ErrorCorrectionLevel.L: (18, [(2, 68)]),
        ErrorCorrectionLevel.M: (16, [(4, 27)]),
        ErrorCorrectionLevel.Q: (24, [(4, 19)]),
        ErrorCorrectionLevel.H: (28, [(4, 15)]),
    },
    7: {
        ErrorCorrectionLevel.L: (20, [(2, 78)]),
        ErrorCorrectionLevel.M: (18, [(4, 31)]),
        ErrorCorrectionLevel.Q: (18, [(2, 14), (4, 15)]),
        ErrorCorrectionLevel.H: (26, [(4, 13), (1, 14)]),
    },
    8: {
        ErrorCorrectionLevel.L: (24, [(2, 97)]),
        ErrorCorrectionLevel.M: (22, [(2, 38), (2, 39)]),
        ErrorCorrectionLevel.Q: (22, [(4, 18), (2, 19)]),
        ErrorCorrectionLevel.H: (26, [(4, 14), (2, 15)]),
    },
    9: {
        ErrorCorrectionLevel.L: (30, [(2, 116)]),
        ErrorCorrectionLevel.M: (22, [(3, 36), (2, 37)]),
        ErrorCorrectionLevel.Q: (20, [(4, 16), (4, 17)]),
        ErrorCorrectionLevel.H: (24, [(4, 12), (4, 13)]),
    },
    10: {
        ErrorCorrectionLevel.L: (18, [(2, 68), (2, 69)]),
        ErrorCorrectionLevel.M: (26, [(4, 43), (1, 44)]),
        ErrorCorrectionLevel.Q: (24, [(6, 19), (2, 20)]),
        ErrorCorrectionLevel.H: (28, [(6, 15), (2, 16)]),
    },
}

# Character count indicator bits based on version
def get_char_count_indicator_bits(version: int, mode: Mode) -> int:
    if 1 <= version <= 9:
        if mode == Mode.NUMERIC: return 10
        if mode == Mode.ALPHANUMERIC: return 9
        if mode == Mode.BYTE: return 8
    elif 10 <= version <= 26:
        if mode == Mode.NUMERIC: return 12
        if mode == Mode.ALPHANUMERIC: return 11
        if mode == Mode.BYTE: return 16
    return 0

ALPHANUMERIC_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"
