"""Data types for Gmail message structure."""

from dataclasses import dataclass


@dataclass
class Headers:
    from_addr: str
    date: str
    subject: str


@dataclass
class Message:
    id: str
    headers: Headers
    html: str | None
    plain: str | None
