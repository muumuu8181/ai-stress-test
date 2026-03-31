from typing import List, Optional, Tuple
from .constants import ALIGNMENT_PATTERNS, ErrorCorrectionLevel

class QRMatrix:
    def __init__(self, version: int):
        self.version = version
        self.size = (version - 1) * 4 + 21
        # None = empty, False = white, True = black
        self.matrix: List[List[Optional[bool]]] = [[None for _ in range(self.size)] for _ in range(self.size)]
        # True if the cell is a functional pattern and cannot be overwritten by data
        self.reserved: List[List[bool]] = [[False for _ in range(self.size)] for _ in range(self.size)]

    def set_module(self, r: int, c: int, val: bool, reserve: bool = False) -> None:
        if 0 <= r < self.size and 0 <= c < self.size:
            self.matrix[r][c] = val
            if reserve:
                self.reserved[r][c] = True

    def place_finder_patterns(self) -> None:
        def place_finder(r_start: int, c_start: int):
            # The pattern is 7x7 plus a 1-module separator
            for r in range(-1, 8):
                for c in range(-1, 8):
                    curr_r, curr_c = r_start + r, c_start + c
                    if 0 <= curr_r < self.size and 0 <= curr_c < self.size:
                        if 0 <= r <= 6 and 0 <= c <= 6:
                            is_black = not (1 <= r <= 5 and 1 <= c <= 5) or (2 <= r <= 4 and 2 <= c <= 4)
                            self.set_module(curr_r, curr_c, is_black, True)
                        else:
                            self.set_module(curr_r, curr_c, False, True)

        place_finder(0, 0)
        place_finder(0, self.size - 7)
        place_finder(self.size - 7, 0)

    def place_alignment_patterns(self) -> None:
        coords = ALIGNMENT_PATTERNS[self.version]
        for r_center in coords:
            for c_center in coords:
                # Skip if it overlaps with finder patterns
                if (r_center <= 10 and c_center <= 10) or \
                   (r_center <= 10 and c_center >= self.size - 11) or \
                   (r_center >= self.size - 11 and c_center <= 10):
                    continue

                for r in range(-2, 3):
                    for c in range(-2, 3):
                        is_black = max(abs(r), abs(c)) != 1
                        self.set_module(r_center + r, c_center + c, is_black, True)

    def place_timing_patterns(self) -> None:
        for i in range(8, self.size - 8):
            val = (i % 2 == 0)
            self.set_module(6, i, val, True)
            self.set_module(i, 6, val, True)

    def place_dark_module(self) -> None:
        # Dark module is at (4*version + 9, 8)
        self.set_module(4 * self.version + 9, 8, True, True)

    def place_format_info(self, ec_level: ErrorCorrectionLevel, mask_pattern: int) -> None:
        # Format info is 15 bits
        # bits 0-1: EC level, bits 2-4: mask pattern, bits 5-14: error correction
        # EC level bits: L=01, M=00, Q=11, H=10
        # Wait, my ErrorCorrectionLevel enum values are: L=1, M=0, Q=3, H=2
        # Which matches the bit patterns!
        data = (ec_level.value << 3) | mask_pattern
        rem = data << 10
        gen = 0x537 # x^10 + x^8 + x^5 + x^4 + x^2 + x + 1
        for i in range(4, -1, -1):
            if rem & (1 << (i + 10)):
                rem ^= gen << i
        format_info = (data << 10) | rem
        format_info ^= 0x5412 # Mask 101010000010010

        # Place format info
        bits = [bool((format_info >> i) & 1) for i in range(15)]

        # Format bits placement:
        # Horizontal: (8,0)-(8,5), (8,7), (8,8), (7,8), (5,8), (4,8), (3,8), (2,8), (1,8), (0,8)
        coords = [
            (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 7), (8, 8),
            (7, 8), (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8)
        ]
        for i in range(15):
            self.set_module(coords[i][0], coords[i][1], bits[i], True)

        # Vertical / other side:
        coords2 = [
            (self.size - 1, 8), (self.size - 2, 8), (self.size - 3, 8), (self.size - 4, 8),
            (self.size - 5, 8), (self.size - 6, 8), (self.size - 7, 8), (8, self.size - 8),
            (8, self.size - 7), (8, self.size - 6), (8, self.size - 5), (8, self.size - 4),
            (8, self.size - 3), (8, self.size - 2), (8, self.size - 1)
        ]
        for i in range(15):
            self.set_module(coords2[i][0], coords2[i][1], bits[i], True)

    def place_data(self, codewords: List[int], mask_pattern: int) -> None:
        bit_idx = 0
        bits = []
        for cw in codewords:
            for i in range(7, -1, -1):
                bits.append(bool((cw >> i) & 1))

        def get_mask(p, r, c):
            if p == 0: return (r + c) % 2 == 0
            if p == 1: return r % 2 == 0
            if p == 2: return c % 3 == 0
            if p == 3: return (r + c) % 3 == 0
            if p == 4: return (r // 2 + c // 3) % 2 == 0
            if p == 5: return ((r * c) % 2) + ((r * c) % 3) == 0
            if p == 6: return (((r * c) % 2) + ((r * c) % 3)) % 2 == 0
            if p == 7: return (((r + c) % 2) + ((r * c) % 3)) % 2 == 0
            return False

        direction = -1 # Up
        c = self.size - 1
        while c > 0:
            if c == 6: # Skip timing pattern column
                c -= 1

            rows = range(self.size - 1, -1, -1) if direction == -1 else range(self.size)
            for r in rows:
                for col_off in range(2):
                    curr_c = c - col_off
                    if not self.reserved[r][curr_c]:
                        val = False
                        if bit_idx < len(bits):
                            val = bits[bit_idx]
                            bit_idx += 1

                        # Apply mask during placement
                        if get_mask(mask_pattern, r, curr_c):
                            val = not val
                        self.set_module(r, curr_c, val)
            c -= 2
            direction *= -1

    def evaluate_score(self) -> int:
        score = 0
        # Rule 1: Same color in row/column
        for r in range(self.size):
            count = 1
            for c in range(1, self.size):
                if self.matrix[r][c] == self.matrix[r][c-1]:
                    count += 1
                else:
                    if count >= 5: score += 3 + (count - 5)
                    count = 1
            if count >= 5: score += 3 + (count - 5)
        for c in range(self.size):
            count = 1
            for r in range(1, self.size):
                if self.matrix[r][c] == self.matrix[r-1][c]:
                    count += 1
                else:
                    if count >= 5: score += 3 + (count - 5)
                    count = 1
            if count >= 5: score += 3 + (count - 5)

        # Rule 2: 2x2 blocks
        for r in range(self.size - 1):
            for c in range(self.size - 1):
                if self.matrix[r][c] == self.matrix[r+1][c] == self.matrix[r][c+1] == self.matrix[r+1][c+1]:
                    score += 3

        # Rule 3: Pattern 1:1:3:1:1
        finder_like = [True, False, True, True, True, False, True]
        for r in range(self.size):
            for c in range(self.size - 6):
                window = [self.matrix[r][c+i] for i in range(7)]
                if window == finder_like:
                    # Check for 4 white modules on either side
                    has_left = (c >= 4 and all(not self.matrix[r][c-i] for i in range(1, 5)))
                    has_right = (c + 7 <= self.size - 4 and all(not self.matrix[r][c+7+i] for i in range(4)))
                    if has_left or has_right:
                        score += 40
        for c in range(self.size):
            for r in range(self.size - 6):
                window = [self.matrix[r+i][c] for i in range(7)]
                if window == finder_like:
                    has_top = (r >= 4 and all(not self.matrix[r-i][c] for i in range(1, 5)))
                    has_bottom = (r + 7 <= self.size - 4 and all(not self.matrix[r+7+i][c] for i in range(4)))
                    if has_top or has_bottom:
                        score += 40

        # Rule 4: Dark module ratio
        dark_count = sum(row.count(True) for row in self.matrix)
        ratio = (dark_count * 100) / (self.size * self.size)
        score += int(abs(ratio - 50) / 5) * 10

        return score

def generate_optimal_matrix(version: int, ec_level: ErrorCorrectionLevel, codewords: List[int]) -> QRMatrix:
    best_score = float('inf')
    best_matrix = None

    for p in range(8):
        m = QRMatrix(version)
        m.place_finder_patterns()
        m.place_alignment_patterns()
        m.place_timing_patterns()
        m.place_dark_module()
        m.place_format_info(ec_level, p)

        m.place_data(codewords, p)

        score = m.evaluate_score()
        if score < best_score:
            best_score = score
            best_matrix = m

    return best_matrix
