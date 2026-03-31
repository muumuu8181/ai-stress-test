import email
from email.message import Message
from email.header import decode_header
from email.utils import getaddresses, formataddr
from typing import Union, List, Optional, Tuple

try:
    from .models import MailMessage, EmailContent, Attachment # type: ignore
except ImportError:
    from models import MailMessage, EmailContent, Attachment # type: ignore

class MailParser:
    """
    A class for parsing MIME email messages.
    """

    @staticmethod
    def parse(raw_email: Union[str, bytes]) -> MailMessage:
        """
        Parses a raw email string or bytes into a MailMessage object.

        Args:
            raw_email: The raw email content as a string or bytes.

        Returns:
            A MailMessage object containing the parsed email data.
        """
        if isinstance(raw_email, str):
            msg = email.message_from_string(raw_email)
        else:
            msg = email.message_from_bytes(raw_email)

        mail_message = MailMessage()

        # Parse headers
        mail_message.subject = MailParser._decode_mime_header(msg.get("Subject", ""))
        mail_message.from_address = MailParser._decode_mime_header(msg.get("From", ""))
        mail_message.to_addresses = MailParser._parse_address_list(msg.get("To", ""))
        mail_message.date = msg.get("Date", "")

        for key, value in msg.items():
            mail_message.headers[key] = MailParser._decode_mime_header(value)

        # Parse body and attachments
        MailParser._parse_payload(msg, mail_message)

        return mail_message

    @staticmethod
    def _decode_mime_header(header_value: str) -> str:
        """Decodes MIME encoded headers."""
        if not header_value:
            return ""

        decoded_parts = decode_header(header_value)
        result = []
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    result.append(part.decode(encoding or "utf-8", errors="replace"))
                except (LookupError, UnicodeDecodeError):
                    result.append(part.decode("latin-1", errors="replace"))
            else:
                result.append(part)
        return "".join(result)

    @staticmethod
    def _parse_address_list(address_header: str) -> List[str]:
        """Parses a comma-separated list of email addresses from a header."""
        if not address_header:
            return []

        # We decode the header first because getaddresses expects a string
        # which might contain MIME encoded words
        decoded_header = MailParser._decode_mime_header(address_header)
        addresses = getaddresses([decoded_header])
        return [formataddr(addr) for addr in addresses]

    @staticmethod
    def _parse_payload(msg: Message, mail_message: MailMessage) -> None:
        """Recursively parses the email payload for body content and attachments."""
        if msg.is_multipart():
            for part in msg.walk():
                # skip the multipart container itself
                if part.get_content_maintype() == 'multipart':
                    continue
                MailParser._process_single_part(part, mail_message)
        else:
            MailParser._process_single_part(msg, mail_message)

    @staticmethod
    def _process_single_part(part: Message, mail_message: MailMessage) -> None:
        """Processes a single part of a MIME message."""
        content_type = part.get_content_type()
        disposition = part.get_content_disposition()
        filename = part.get_filename()

        # If it has a filename or is marked as attachment, treat it as an attachment
        if filename or disposition == 'attachment':
            payload = part.get_payload(decode=True)
            if payload is not None:
                filename = MailParser._decode_mime_header(filename) if filename else "unnamed"
                mail_message.attachments.append(Attachment(
                    filename=filename,
                    content_type=content_type,
                    content=payload,
                    content_id=part.get("Content-ID")
                ))
        elif content_type == "text/plain":
            payload = part.get_payload(decode=True)
            if isinstance(payload, bytes):
                charset = part.get_content_charset() or "utf-8"
                try:
                    mail_message.content.text = payload.decode(charset, errors="replace")
                except (LookupError, UnicodeDecodeError):
                    mail_message.content.text = payload.decode("latin-1", errors="replace")
        elif content_type == "text/html":
            payload = part.get_payload(decode=True)
            if isinstance(payload, bytes):
                charset = part.get_content_charset() or "utf-8"
                try:
                    mail_message.content.html = payload.decode(charset, errors="replace")
                except (LookupError, UnicodeDecodeError):
                    mail_message.content.html = payload.decode("latin-1", errors="replace")
        else:
            # If it's not text/plain or text/html and not explicitly an attachment,
            # it might still be an attachment (e.g. image/png without disposition)
            payload = part.get_payload(decode=True)
            if payload is not None:
                filename = MailParser._decode_mime_header(filename) if filename else "unnamed"
                mail_message.attachments.append(Attachment(
                    filename=filename,
                    content_type=content_type,
                    content=payload,
                    content_id=part.get("Content-ID")
                ))
