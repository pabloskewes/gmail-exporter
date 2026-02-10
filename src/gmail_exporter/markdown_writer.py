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


def _replace_cids(
    html: str, cid_mapping: dict[str, str]
) -> str:
    """Replace cid: references with local file paths."""
    if not html or not cid_mapping:
        return html

    # Pattern: src="cid:ii_miid2twg0" or similar
    def replacer(match: re.Match) -> str:
        cid = match.group(1)
        if cid in cid_mapping:
            return f'src="{cid_mapping[cid]}"'
        return match.group(0)  # Keep original if not found

    return re.sub(r'src="cid:([^"]+)"', replacer, html)


def thread_to_markdown(
    messages: list[Message], subject: str, cid_mapping: dict[str, str] | None = None
) -> str:
    """Build a single Markdown document from cleaned messages."""
    if not messages:
        return f"# {subject}\n\n(No messages)\n"

    cid_mapping = cid_mapping or {}
    lines = [f"# {subject}", "", "---", ""]

    for m in messages:
        lines.extend(
            [
                f"**From:** {m.from_addr}  ",
                f"**Date:** {m.date}",
                "",
            ]
        )

        # Replace CIDs in HTML before converting to markdown
        html_content = m.body_html
        if html_content and cid_mapping:
            html_content = _replace_cids(html_content, cid_mapping)

        content = _html_to_markdown(html_content) if html_content else m.body_plain
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
