"""CLI entry point for Gmail thread exporter."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer

from gmail_exporter.attachment_handler import save_attachments
from gmail_exporter.auth import get_gmail_service
from gmail_exporter.gmail_client import get_thread_messages
from gmail_exporter.markdown_writer import save_thread, thread_to_markdown
from gmail_exporter.parser import extract_message

app = typer.Typer()

TRUNCATE = 1200


def _truncate(s: str | None) -> str | None:
    if s is None:
        return None
    if len(s) <= TRUNCATE:
        return s
    return s[:TRUNCATE] + "\n\n... [truncated]"


@app.callback(invoke_without_command=True)
def main(
    thread_id: str = typer.Argument(
        ..., help="Gmail thread ID to export (find in thread URL)"
    ),
    output_dir: Path = typer.Option(
        Path("./exports"),
        "--output-dir",
        "-o",
        path_type=Path,
        help="Output directory for .md files",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Pretty-print raw message data. Use: gmail-exporter --debug THREAD_ID",
    ),
) -> None:
    """Export Gmail threads to Markdown files.

    Thread ID can be found in the Gmail URL when viewing a thread.
    """
    try:
        print("✓ Authenticating...")
        service = get_gmail_service()
        print("✓ Authenticated successfully")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        raise typer.Exit(1)

    try:
        print(f"✓ Fetching thread: {thread_id}")
        messages = get_thread_messages(service, thread_id)
    except Exception as e:
        print(f"Error fetching thread: {e}", file=sys.stderr)
        raise typer.Exit(1)

    if not messages:
        print("No messages in thread.", file=sys.stderr)
        raise typer.Exit(1)

    print(f"✓ Found {len(messages)} messages")

    if debug:
        to_print = []
        for m in messages:
            to_print.append(
                {
                    "id": m.id,
                    "headers": {
                        "From": m.headers.from_addr,
                        "Date": m.headers.date,
                        "Subject": m.headers.subject,
                    },
                    "html_len": len(m.html) if m.html else 0,
                    "plain_len": len(m.plain) if m.plain else 0,
                    "html_preview": _truncate(m.html),
                    "plain_preview": _truncate(m.plain),
                }
            )
        print(json.dumps(to_print, indent=2, ensure_ascii=False))
        return

    parsed = [extract_message(m) for m in messages]
    for i, m in enumerate(parsed, 1):
        print(f"✓ Processing message {i}/{len(parsed)} from {m.from_addr}")

    # Download attachments and build CID mapping (with deduplication)
    print("✓ Downloading attachments...")
    cid_mapping: dict[str, str] = {}
    dedup_cache: dict[str, str] = {}
    for raw_msg, parsed_msg in zip(messages, parsed):
        if parsed_msg.attachments:
            msg_mapping = save_attachments(
                service,
                raw_msg.id,
                parsed_msg.attachments,
                output_dir,
                thread_id,
                dedup_cache,
            )
            cid_mapping.update(msg_mapping)
            print(f"  → Processed {len(parsed_msg.attachments)} attachment(s)")

    if dedup_cache:
        print(f"  → Saved {len(dedup_cache)} unique image(s)")

    subject = parsed[0].subject if parsed else "Thread Export"
    md_content = thread_to_markdown(parsed, subject, cid_mapping)
    out_path = save_thread(md_content, subject, output_dir)
    print(f"✓ Exported to: {out_path}")


if __name__ == "__main__":
    app()
