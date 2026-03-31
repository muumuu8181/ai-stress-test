from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class Attachment:
    """
    Represents an email attachment.

    Attributes:
        filename: The name of the attached file.
        content_type: The MIME type of the file.
        content: The binary content of the file.
        content_id: Optional Content-ID for inline attachments.
    """
    filename: Optional[str]
    content_type: str
    content: bytes
    content_id: Optional[str] = None

@dataclass
class EmailContent:
    """
    Represents the body of an email.

    Attributes:
        text: The plain text version of the email body.
        html: The HTML version of the email body.
    """
    text: Optional[str] = None
    html: Optional[str] = None

@dataclass
class MailMessage:
    """
    Represents a parsed email message.

    Attributes:
        subject: The subject of the email.
        from_address: The sender's email address.
        to_addresses: A list of recipient email addresses.
        date: The date the email was sent.
        headers: A dictionary containing all email headers.
        content: The EmailContent object containing text and html bodies.
        attachments: A list of Attachment objects.
    """
    subject: str = ""
    from_address: str = ""
    to_addresses: List[str] = field(default_factory=list)
    date: str = ""
    headers: Dict[str, List[str]] = field(default_factory=dict)
    content: EmailContent = field(default_factory=EmailContent)
    attachments: List[Attachment] = field(default_factory=list)
