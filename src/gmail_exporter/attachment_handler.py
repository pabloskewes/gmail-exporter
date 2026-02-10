"""Download and save Gmail attachments (inline images)."""

import base64
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
) -> dict[str, str]:
    """
    Download and save attachments to disk.

    Returns a mapping of content_id -> relative_path for use in markdown.
    """
    if not attachments:
        return {}

    # Create images subdirectory
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    cid_to_path: dict[str, str] = {}

    for i, attachment in enumerate(attachments):
        # Infer extension from mime type
        ext = _get_extension(attachment.mime_type, attachment.filename)

        # Generate unique filename: thread_id_msg_index_attachment_index.ext
        filename = f"{thread_id}_{message_id[:8]}_{i}{ext}"
        file_path = images_dir / filename

        # Download and save
        data = download_attachment(
            service, "me", message_id, attachment.attachment_id
        )
        file_path.write_bytes(data)

        # Store relative path for markdown (relative to output_dir)
        relative_path = f"./images/{filename}"
        cid_to_path[attachment.content_id] = relative_path

    return cid_to_path


def _get_extension(mime_type: str, filename: str) -> str:
    """Get file extension from mime type or filename."""
    # Try to get from filename first
    if "." in filename:
        return Path(filename).suffix

    # Fallback to mime type
    mime_to_ext = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/svg+xml": ".svg",
    }
    return mime_to_ext.get(mime_type, ".bin")
