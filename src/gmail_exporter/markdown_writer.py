"""Markdown generation and file output."""

import re
from pathlib import Path

from markdownify import markdownify as md

from gmail_exporter.types import Message


def _html_to_markdown(html: str) -> str:
    """Convert HTML to Markdown via markdownify."""
    if not html or not html.strip():
        return ""
    return md(
        html,
        heading_style="ATX",
        escape_asterisks=False,
        escape_underscores=False,
    )


def thread_to_markdown(messages: list[Message], subject: str) -> str:
    """Build a single Markdown document from cleaned messages."""
    if not messages:
        return f"# {subject}\n\n(No messages)\n"

    lines = [f"# {subject}", "", "---", ""]

    for m in messages:
        lines.extend(
            [
                f"**From:** {m.from_addr}  ",
                f"**Date:** {m.date}",
                "",
            ]
        )
        content = _html_to_markdown(m.body_html) if m.body_html else m.body_plain
        if content.strip():
            lines.append(content.strip())
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines).rstrip()


def sanitize_filename(subject: str) -> str:
    """Make a safe filename from subject."""
    if not subject or not subject.strip():
        return "thread_export"
    safe = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", subject)
    safe = re.sub(r"[\s_]+", "_", safe)
    return safe[:200].strip("_") or "thread_export"


def save_thread(content: str, subject: str, output_dir: Path) -> Path:
    """Write Markdown to file. Returns path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = sanitize_filename(subject) + ".md"
    path = output_dir / filename
    path.write_text(content, encoding="utf-8")
    return path
