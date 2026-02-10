"""Gmail API client for fetching threads and messages.

Handles the Gmail API structure including multipart MIME messages.
Messages can have nested structures: multipart/alternative (plain + html),
multipart/mixed (with attachments). This module recursively extracts
text/html and text/plain parts from any nesting level.
"""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource


def _decode_body(data: str | None) -> str:
    """Decode base64url-encoded body data from Gmail API."""
    if not data:
        return ""
    try:
        decoded = base64.urlsafe_b64decode(data)
        return decoded.decode("utf-8", errors="replace")
    except (ValueError, UnicodeDecodeError):
        return ""


def get_message_parts(payload: dict[str, Any]) -> dict[str, str | None]:
    """Extract text/html and text/plain from a message payload.

    Navigates the recursive MIME structure. Gmail messages can have:
    - multipart/alternative: typically contains text/plain and text/html
    - multipart/mixed: may wrap alternative + attachments
    - Nested parts at arbitrary depth

    Returns dict with keys 'text/html' and 'text/plain', values are
    decoded strings or None if that part is not found.
    """
    parts: dict[str, str | None] = {"text/html": None, "text/plain": None}

    if "parts" in payload:
        for part in payload["parts"]:
            mime_type = part.get("mimeType", "")
            if mime_type in ("text/html", "text/plain"):
                body_data = part.get("body", {}).get("data")
                if body_data:
                    parts[mime_type] = _decode_body(body_data)
            elif "parts" in part:
                # Recurse into nested multipart
                nested = get_message_parts(part)
                for k, v in nested.items():
                    if v is not None:
                        parts[k] = v
    else:
        # Single-part message
        mime_type = payload.get("mimeType", "")
        body_data = payload.get("body", {}).get("data")
        if mime_type in ("text/html", "text/plain") and body_data:
            parts[mime_type] = _decode_body(body_data)

    return parts


def _get_header(headers: list[dict[str, str]], name: str) -> str:
    """Get header value by name (case-insensitive)."""
    name_lower = name.lower()
    for h in headers:
        if h.get("name", "").lower() == name_lower:
            return h.get("value", "")
    return ""


def get_thread_messages(service: Resource, thread_id: str) -> list[dict[str, Any]]:
    """Fetch a thread with full message data and extract content.

    Returns a list of message dicts, each with:
    - headers: dict with From, Date, Subject
    - html: str | None - raw HTML body
    - plain: str | None - raw plain text body
    """
    thread = (
        service.users()
        .threads()
        .get(userId="me", id=thread_id, format="full")
        .execute()
    )

    messages = thread.get("messages", [])
    result: list[dict[str, Any]] = []

    for msg in messages:
        payload = msg.get("payload", {})
        headers_list = payload.get("headers", [])
        headers = {
            "From": _get_header(headers_list, "From"),
            "Date": _get_header(headers_list, "Date"),
            "Subject": _get_header(headers_list, "Subject"),
        }
        parts = get_message_parts(payload)

        result.append(
            {
                "id": msg.get("id"),
                "headers": headers,
                "html": parts.get("text/html"),
                "plain": parts.get("text/plain"),
            }
        )

    return result
