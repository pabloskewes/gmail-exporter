"""Gmail API: fetch threads and extract message content from MIME parts."""

import base64
from typing import Any

from googleapiclient.discovery import Resource

from gmail_exporter.types import Attachment, Headers, RawMessage


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


def _extract_attachments(payload: dict[str, Any]) -> list[Attachment]:
    """Extract inline attachments (images) with Content-ID from payload."""
    attachments: list[Attachment] = []

    def _walk_parts(part: dict[str, Any]) -> None:
        # Check if this part has an attachment
        body = part.get("body", {})
        attachment_id = body.get("attachmentId")
        mime_type = part.get("mimeType", "")
        filename = part.get("filename", "")

        # Look for Content-ID header (indicates inline attachment)
        content_id = None
        if "headers" in part:
            for header in part["headers"]:
                if header.get("name", "").lower() == "content-id":
                    # Content-ID comes as "<ii_miid2twg0>", strip angle brackets
                    cid = header.get("value", "")
                    content_id = cid.strip("<>")
                    break

        # If has attachment_id and content_id, it's an inline image
        if attachment_id and content_id:
            attachments.append(
                Attachment(
                    content_id=content_id,
                    attachment_id=attachment_id,
                    filename=filename or "attachment",
                    mime_type=mime_type,
                    size=body.get("size", 0),
                )
            )

        # Recurse into nested parts
        if "parts" in part:
            for subpart in part["parts"]:
                _walk_parts(subpart)

    _walk_parts(payload)
    return attachments


def get_thread_messages(service: Resource, thread_id: str) -> list[RawMessage]:
    """Fetch thread and return list of Message per message."""
    thread = (
        service.users()
        .threads()
        .get(userId="me", id=thread_id, format="full")
        .execute()
    )
    messages = thread.get("messages", [])

    result: list[RawMessage] = []
    for msg in messages:
        payload = msg.get("payload", {})
        headers_list = payload.get("headers", [])
        parts = get_message_parts(payload)
        attachments = _extract_attachments(payload)
        result.append(
            RawMessage(
                id=msg.get("id", ""),
                headers=Headers(
                    from_addr=_get_header(headers_list, "From"),
                    date=_get_header(headers_list, "Date"),
                    subject=_get_header(headers_list, "Subject"),
                ),
                html=parts.get("text/html"),
                plain=parts.get("text/plain"),
                attachments=attachments,
            )
        )
    return result
