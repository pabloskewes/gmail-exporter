"""Markdown generation and file output for exported threads."""

from __future__ import annotations

import re
from pathlib import Path

from markdownify import markdownify as md


def _html_to_markdown(html: str) -> str:
    """Convert HTML to Markdown, preserving code blocks."""
    if not html or not html.strip():
        return ""
    return md(
        html, heading_style="ATX", escape_asterisks=False, escape_underscores=False
    )


def thread_to_markdown(messages: list[dict], subject: str) -> str:
    """Convert a list of message dicts to a single Markdown document.

    Each message dict should have: from, date, subject, body_html, body_plain.
    Uses body_html when available (converts via markdownify), else body_plain.
    """
    if not messages:
        return f"# {subject}\n\n(No messages)\n"

    lines = [f"# {subject}", "", "---", ""]

    for msg in messages:
        from_addr = msg.get("from", "")
        date = msg.get("date", "")
        body_html = msg.get("body_html", "")
        body_plain = msg.get("body_plain", "")

        lines.extend(
            [
                f"**From:** {from_addr}  ",
                f"**Date:** {date}",
                "",
            ]
        )

        if body_html:
            content = _html_to_markdown(body_html)
        else:
            content = body_plain or ""

        if content.strip():
            lines.append(content.strip())
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines).rstrip()


def sanitize_filename(subject: str) -> str:
    """Convert email subject to a safe filename (no path separators or special chars)."""
    if not subject or not subject.strip():
        return "thread_export"
    # Replace problematic chars with underscore
    safe = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", subject)
    # Collapse multiple underscores/spaces
    safe = re.sub(r"[\s_]+", "_", safe)
    # Limit length
    return safe[:200].strip("_") or "thread_export"


def save_thread(markdown_content: str, subject: str, output_dir: str | Path) -> Path:
    """Save thread content to a .md file in the output directory."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    filename = sanitize_filename(subject) + ".md"
    filepath = output_path / filename
    filepath.write_text(markdown_content, encoding="utf-8")
    return filepath
