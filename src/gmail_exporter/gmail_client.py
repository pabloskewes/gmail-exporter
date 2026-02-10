"""Gmail API: fetch threads and extract message content from MIME parts."""

import base64
from typing import Any

from googleapiclient.discovery import Resource

from gmail_exporter.types import Headers, Message


def _decode(data: str) -> str:
    """Decode base64url body from Gmail API."""
    if not data:
        return ""
    raw = base64.urlsafe_b64decode(data)
    return raw.decode("utf-8", errors="replace")


def _get_header(headers: list[dict], name: str) -> str:
    """Get header value by name, case-insensitive."""
    name = name.lower()
    for h in headers:
        if h.get("name", "").lower() == name:
            return h.get("value", "")
    return ""


def get_message_parts(payload: dict[str, Any]) -> dict[str, str | None]:
    """Extract text/html and text/plain from payload. Walks nested MIME parts."""
    out: dict[str, str | None] = {"text/html": None, "text/plain": None}

    if "parts" in payload:
        for part in payload["parts"]:
            mime = part.get("mimeType", "")
            if mime in ("text/html", "text/plain"):
                data = part.get("body", {}).get("data")
                if data:
                    out[mime] = _decode(data)
            else:
                nested = get_message_parts(part)
                out.update({k: v for k, v in nested.items() if v is not None})
        return out

    mime = payload.get("mimeType", "")
    data = payload.get("body", {}).get("data")
    if mime in ("text/html", "text/plain") and data:
        out[mime] = _decode(data)
    return out


def get_thread_messages(service: Resource, thread_id: str) -> list[Message]:
    """Fetch thread and return list of Message per message."""
    thread = (
        service.users()
        .threads()
        .get(userId="me", id=thread_id, format="full")
        .execute()
    )
    messages = thread.get("messages", [])

    result: list[Message] = []
    for msg in messages:
        payload = msg.get("payload", {})
        headers_list = payload.get("headers", [])
        parts = get_message_parts(payload)
        result.append(
            Message(
                id=msg.get("id", ""),
                headers=Headers(
                    from_addr=_get_header(headers_list, "From"),
                    date=_get_header(headers_list, "Date"),
                    subject=_get_header(headers_list, "Subject"),
                ),
                html=parts.get("text/html"),
                plain=parts.get("text/plain"),
            )
        )
    return result
