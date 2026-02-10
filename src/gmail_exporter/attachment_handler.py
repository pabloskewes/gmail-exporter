"""Download and save Gmail attachments (inline images)."""

import base64
import hashlib
from pathlib import Path

from googleapiclient.discovery import Resource

from gmail_exporter.types import Attachment


def download_attachment(
    service: Resource, user_id: str, message_id: str, attachment_id: str
) -> bytes:
    """Download attachment data from Gmail API."""
    attachment = (
        service.users()
        .messages()
        .attachments()
        .get(userId=user_id, messageId=message_id, id=attachment_id)
        .execute()
    )
    data = attachment.get("data", "")
    return base64.urlsafe_b64decode(data)


def save_attachments(
    service: Resource,
    message_id: str,
    attachments: list[Attachment],
    output_dir: Path,
    thread_id: str,
    dedup_cache: dict[str, str],
) -> dict[str, str]:
    """Download attachments to disk. Uses content hash for deduplication. Returns content_id -> relative_path mapping."""
    if not attachments:
        return {}

    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    cid_to_path: dict[str, str] = {}

    for i, attachment in enumerate(attachments):
        data = download_attachment(
            service, "me", message_id, attachment.attachment_id
        )
        content_hash = hashlib.sha256(data).hexdigest()

        if content_hash in dedup_cache:
            relative_path = dedup_cache[content_hash]
        else:
            ext = _get_extension(attachment.mime_type, attachment.filename)
            filename = f"{thread_id}_{message_id[:8]}_{i}{ext}"
            file_path = images_dir / filename
            file_path.write_bytes(data)
            relative_path = f"./images/{filename}"
            dedup_cache[content_hash] = relative_path

        cid_to_path[attachment.content_id] = relative_path

    return cid_to_path


def _get_extension(mime_type: str, filename: str) -> str:
    """Get file extension from mime type or filename."""
    if "." in filename:
        return Path(filename).suffix
    mime_to_ext = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/svg+xml": ".svg",
    }
    return mime_to_ext.get(mime_type, ".bin")
