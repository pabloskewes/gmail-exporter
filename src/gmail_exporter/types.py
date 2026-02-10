"""Data types for Gmail message structure."""

from dataclasses import dataclass


@dataclass
class Headers:
    from_addr: str
    date: str
    subject: str


@dataclass
class RawMessage:
    id: str
    headers: Headers
    html: str | None
    plain: str | None


@dataclass
class Message:
    """Cleaned message, ready for Markdown export."""

    from_addr: str
    date: str
    subject: str
    body_html: str
    body_plain: str
