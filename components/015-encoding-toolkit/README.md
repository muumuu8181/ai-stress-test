# Encoding & Hash Toolkit (`enctool`)

A simple toolkit for various encoding and hashing tasks, built using only the Python standard library.

## Features

- **Base64**: Standard and URL-safe encoding/decoding.
- **URL**: URL encoding/decoding.
- **Hex**: Hexadecimal encoding/decoding.
- **ROT13**: ROT13 transformation.
- **Hash**: MD5, SHA-1, SHA-256 calculation (supports strings and files).
- **HMAC**: HMAC calculation using MD5, SHA-1, or SHA-256.
- **CRC32**: CRC32 checksum calculation.
- **Charset**:
    - Convert text encoding (UTF-8, Shift-JIS, EUC-JP, etc.).
    - Detect text encoding (heuristic).

## Installation

```bash
# From the component directory
pip install .
```

## Usage

### CLI Examples

#### Base64
```bash
python -m enctool base64 encode "hello"
# aGVsbG8=

python -m enctool base64 decode "aGVsbG8="
# hello

python -m enctool base64 encode "data" --url-safe
```

#### Hash & HMAC
```bash
python -m enctool hash sha256 "hello"
# 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824

python -m enctool hash md5 file.txt --file

python -m enctool hmac sha256 "mysecretkey" "message"
```

#### URL & Hex
```bash
python -m enctool url encode "hello world"
# hello%20world

python -m enctool hex encode "hello"
# 68656c6c6f
```

#### ROT13 & CRC32
```bash
python -m enctool rot13 "hello"
# uryyb

python -m enctool crc32 "hello"
# 3610a686
```

#### Charset Detection & Conversion
```bash
python -m enctool detect file.txt
# utf-8

python -m enctool convert file.txt --from-enc utf-8 --to-enc shift-jis > file_sjis.txt
```

## Development

### Running Tests
```bash
pytest --cov=enctool tests/
```

### Linting
```bash
ruff check enctool tests
```
