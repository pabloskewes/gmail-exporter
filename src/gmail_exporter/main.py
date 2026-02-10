"""CLI entry point for Gmail thread exporter."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from gmail_exporter.auth import get_gmail_service
from gmail_exporter.gmail_client import get_thread_messages

app = typer.Typer()


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
    # TODO: parse, markdown, save (parser, markdown_writer)
    for i, m in enumerate(messages, 1):
        from_addr = m.get("headers", {}).get("From", "?")
        print(f"  {i}. {from_addr}")


if __name__ == "__main__":
    app()
