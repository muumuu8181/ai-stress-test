# MIME Mail Parser

A comprehensive Python library and CLI tool for parsing MIME email messages.

## Features

- Support for multipart messages (mixed, alternative, related).
- Automatic decoding of various encodings (Base64, Quoted-Printable).
- Header decoding (including UTF-8 and other character sets).
- Extraction of text and HTML bodies.
- Attachment extraction with metadata.
- CLI for batch processing or piping.

## Installation

```bash
pip install .
```

## Usage

### As a Library

```python
from mail_parser.parser import MailParser

raw_email = """Subject: Hello
From: sender@example.com
To: recipient@example.com

This is a test email body.
"""

mail = MailParser.parse(raw_email)

print(f"Subject: {mail.subject}")
print(f"From: {mail.from_address}")
print(f"Body: {mail.content.text}")

for attachment in mail.attachments:
    print(f"Attachment: {attachment.filename} ({attachment.content_type})")
```

### As a CLI

```bash
# Parse an email file and output JSON
python3 -m mail_parser.cli sample.eml -o output.json

# Parse from stdin
cat sample.eml | python3 -m mail_parser.cli -

# Extract attachments to a directory
python3 -m mail_parser.cli sample.eml -a ./attachments
```

## Running Tests

```bash
pytest
```
