# QR Encoder

A basic QR code generator built using only the Python standard library.

## Features

- QR Code Versions 1-10
- Reed-Solomon Error Correction (L, M, Q, H)
- All 8 Mask Patterns with optimal pattern selection
- Functional patterns: Finder, Timing, Alignment, Dark Module
- Encoding Modes: Numeric, Alphanumeric, Byte
- Output Formats:
  - ASCII (using ■ and □)
  - PBM (Portable BitMap) image

## Installation

This component has no external dependencies. Just copy the `qr_encoder` directory into your project.

## Usage

### Generating a QR Code

```python
from qr_encoder import generate_qr, to_ascii, to_pbm, ErrorCorrectionLevel

# Generate a QR code matrix
data = "https://example.com"
qr = generate_qr(data, ec_level=ErrorCorrectionLevel.H)

# Output as ASCII
print(to_ascii(qr))

# Output as PBM file
pbm_data = to_pbm(qr)
with open("qrcode.pbm", "w") as f:
    f.write(pbm_data)
```

## API Reference

### `generate_qr(data: str, ec_level: ErrorCorrectionLevel = ErrorCorrectionLevel.M) -> QRMatrix`
Generates a QR code for the given data. Automatically selects the best encoding mode and smallest possible version (1-10).

### `to_ascii(matrix: QRMatrix) -> str`
Renders the QR matrix as an ASCII string with a quiet zone.

### `to_pbm(matrix: QRMatrix) -> str`
Renders the QR matrix as a PBM (P1) format string with a quiet zone.

### `ErrorCorrectionLevel`
- `L`: 7% correction
- `M`: 15% correction
- `Q`: 25% correction
- `H`: 30% correction

## Testing

Run tests using `pytest`:

```bash
export PYTHONPATH=$PYTHONPATH:.
pytest tests/
```
