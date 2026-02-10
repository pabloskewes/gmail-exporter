"""CLI entry point for Gmail thread exporter."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from gmail_exporter.auth import get_gmail_service

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

    # TODO: fetch, parse, markdown, save (gmail_client, parser, markdown_writer)
    print(f"thread_id={thread_id}, output_dir={output_dir}")
    _ = service  # suppress unused


if __name__ == "__main__":
    app()
