import pytest
from parser import MailParser
from models import MailMessage, Attachment

def test_parse_simple_text_email():
    raw_email = (
        "Subject: Hello World\r\n"
        "From: sender@example.com\r\n"
        "To: recipient@example.com\r\n"
        "Date: Mon, 1 Jan 2024 10:00:00 +0000\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        "\r\n"
        "This is a test email body."
    )
    mail = MailParser.parse(raw_email)

    assert mail.subject == "Hello World"
    assert mail.from_address == "sender@example.com"
    assert mail.to_addresses == ["recipient@example.com"]
    assert mail.content.text == "This is a test email body."
    assert mail.content.html is None
    assert len(mail.attachments) == 0

def test_parse_encoded_subject():
    raw_email = "Subject: =?utf-8?B?44GT44KT44Gr44Gh44Gv?= World\r\n\r\n"
    mail = MailParser.parse(raw_email)
    assert mail.subject == "こんにちは World"

def test_parse_multipart_mixed_with_attachment():
    raw_email = (
        "Subject: Multipart Test\r\n"
        "MIME-Version: 1.0\r\n"
        "Content-Type: multipart/mixed; boundary=boundary123\r\n"
        "\r\n"
        "--boundary123\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        "\r\n"
        "Text content\r\n"
        "--boundary123\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        "\r\n"
        "<b>HTML content</b>\r\n"
        "--boundary123\r\n"
        "Content-Type: application/octet-stream; name=\"test.bin\"\r\n"
        "Content-Transfer-Encoding: base64\r\n"
        "Content-Disposition: attachment; filename=\"test.bin\"\r\n"
        "\r\n"
        "SGVsbG8gQXR0YWNobWVudA==\r\n"
        "--boundary123--"
    )
    mail = MailParser.parse(raw_email)

    assert mail.content.text == "Text content"
    assert mail.content.html == "<b>HTML content</b>"
    assert len(mail.attachments) == 1
    assert mail.attachments[0].filename == "test.bin"
    assert mail.attachments[0].content == b"Hello Attachment"

def test_parse_edge_cases():
    # Empty input
    mail = MailParser.parse("")
    assert mail.subject == ""
    assert not mail.content.text

    # Missing headers
    mail = MailParser.parse("\r\nBody with no headers")
    assert mail.content.text == "Body with no headers"

    # Multiple recipients
    raw_email = "To: one@example.com, \"Two\" <two@example.com>\r\n\r\n"
    mail = MailParser.parse(raw_email)
    assert mail.to_addresses == ["one@example.com", "Two <two@example.com>"]

def test_parse_quoted_printable():
    raw_email = (
        "Content-Type: text/plain; charset=utf-8\r\n"
        "Content-Transfer-Encoding: quoted-printable\r\n"
        "\r\n"
        "H=C3=A9llo World"
    )
    mail = MailParser.parse(raw_email)
    assert mail.content.text == "Héllo World"

def test_nested_multiparts():
    raw_email = (
        "Content-Type: multipart/mixed; boundary=outer\r\n"
        "\r\n"
        "--outer\r\n"
        "Content-Type: multipart/alternative; boundary=inner\r\n"
        "\r\n"
        "--inner\r\n"
        "Content-Type: text/plain\r\n"
        "\r\n"
        "Alternative text\r\n"
        "--inner\r\n"
        "Content-Type: text/html\r\n"
        "\r\n"
        "Alternative html\r\n"
        "--inner--\r\n"
        "--outer\r\n"
        "Content-Type: image/png; name=img.png\r\n"
        "Content-Transfer-Encoding: base64\r\n"
        "\r\n"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==\r\n"
        "--outer--"
    )
    mail = MailParser.parse(raw_email)
    assert mail.content.text == "Alternative text"
    assert mail.content.html == "Alternative html"
    assert len(mail.attachments) == 1
    assert mail.attachments[0].filename == "img.png"
    assert mail.attachments[0].content_type == "image/png"

def test_repeated_headers():
    raw_email = (
        "Received: from a.com\r\n"
        "Received: from b.com\r\n"
        "Subject: Multi-headers\r\n\r\n"
    )
    mail = MailParser.parse(raw_email)
    assert len(mail.headers["Received"]) == 2
    assert "from a.com" in mail.headers["Received"]
    assert "from b.com" in mail.headers["Received"]

def test_encoded_display_name_with_comma():
    # =?UTF-8?Q?Doe=2C_John?= is "Doe, John"
    raw_email = "To: =?UTF-8?Q?Doe=2C_John?= <john@example.com>\r\n\r\n"
    mail = MailParser.parse(raw_email)
    assert mail.to_addresses == ["Doe, John <john@example.com>"]

def test_rfc822_attachment():
    raw_email = (
        "Subject: Outer email\r\n"
        "Content-Type: multipart/mixed; boundary=outer\r\n\r\n"
        "--outer\r\n"
        "Content-Type: text/plain\r\n\r\n"
        "Outer body text\r\n"
        "--outer\r\n"
        "Content-Type: message/rfc822\r\n"
        "Content-Disposition: attachment; filename=\"inner.eml\"\r\n\r\n"
        "Subject: Inner email\r\n"
        "Content-Type: text/plain\r\n\r\n"
        "Inner body text\r\n"
        "--outer--"
    )
    mail = MailParser.parse(raw_email)
    # The outer body should NOT be overwritten by the inner body
    assert mail.content.text == "Outer body text"
    assert len(mail.attachments) == 1
    assert mail.attachments[0].filename == "inner.eml"
    assert b"Inner body text" in mail.attachments[0].content
