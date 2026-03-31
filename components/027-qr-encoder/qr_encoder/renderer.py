from .matrix import QRMatrix

def to_ascii(matrix: QRMatrix) -> str:
    """
    Renders the QR matrix as an ASCII string using ■ and □.

    Args:
        matrix: The QR matrix to render.

    Returns:
        The ASCII representation of the QR code.
    """
    lines = []
    # Add quiet zone (4 modules)
    quiet_zone = 4
    for _ in range(quiet_zone):
        lines.append("□" * (matrix.size + 2 * quiet_zone))

    for r in range(matrix.size):
        line = ["□" * quiet_zone]
        for c in range(matrix.size):
            line.append("■" if matrix.matrix[r][c] else "□")
        line.append("□" * quiet_zone)
        lines.append("".join(line))

    for _ in range(quiet_zone):
        lines.append("□" * (matrix.size + 2 * quiet_zone))

    return "\n".join(lines)

def to_pbm(matrix: QRMatrix) -> str:
    """
    Renders the QR matrix as a PBM (Portable BitMap) image string.
    PBM (P1) is a plain text format.

    Args:
        matrix: The QR matrix to render.

    Returns:
        The PBM representation of the QR code.
    """
    quiet_zone = 4
    full_size = matrix.size + 2 * quiet_zone
    res = [f"P1", f"{full_size} {full_size}"]

    # Quiet zone top
    for _ in range(quiet_zone):
        res.append(" ".join(["0"] * full_size))

    for r in range(matrix.size):
        row = ["0"] * quiet_zone
        for c in range(matrix.size):
            row.append("1" if matrix.matrix[r][c] else "0")
        row.extend(["0"] * quiet_zone)
        res.append(" ".join(row))

    # Quiet zone bottom
    for _ in range(quiet_zone):
        res.append(" ".join(["0"] * full_size))

    return "\n".join(res) + "\n"
