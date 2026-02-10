"""Data types for Gmail message structure."""

from dataclasses import dataclass, field


@dataclass
class Headers:
    from_addr: str
    date: str
    subject: str


@dataclass
class Attachment:
    """Represents an inline image or attachment."""

    content_id: str  # CID without angle brackets (e.g., "ii_miid2twg0")
    attachment_id: str  # Gmail API attachment ID for downloading
    filename: str  # Original filename
    mime_type: str  # e.g., "image/png"
    size: int  # Size in bytes


@dataclass
class RawMessage:
    id: str
    headers: Headers
    html: str | None
    plain: str | None
    attachments: list[Attachment] = field(default_factory=list)


@dataclass
class Message:
    """Cleaned message, ready for Markdown export."""

    from_addr: str
    date: str
    subject: str
    body_html: str
    body_plain: str
    attachments: list[Attachment] = field(default_factory=list)
