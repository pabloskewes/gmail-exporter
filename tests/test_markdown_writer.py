"""Unit tests for markdown_writer."""

from pathlib import Path

from gmail_exporter.markdown_writer import sanitize_filename, save_thread, thread_to_markdown
from gmail_exporter.types import Message


def test_thread_to_markdown():
    msgs = [
        Message(
            from_addr="a@b.com",
            date="Mon 1 Jan",
            subject="Test",
            body_html="<p>Hello</p>",
            body_plain="",
        ),
    ]
    out = thread_to_markdown(msgs, "Test Subject")
    assert "# Test Subject" in out
    assert "a@b.com" in out
    assert "Hello" in out
    assert "---" in out


def test_sanitize_filename():
    assert sanitize_filename("Hello World") == "Hello_World"
    assert sanitize_filename('Test: "quotes"') == "Test_quotes"
    assert sanitize_filename("") == "thread_export"


def test_save_thread(tmp_path: Path):
    msgs = [
        Message(
            from_addr="x@y.com",
            date="Today",
            subject="My Thread",
            body_html="",
            body_plain="Hi",
        ),
    ]
    content = thread_to_markdown(msgs, "My Thread")
    path = save_thread(content, "My Thread", tmp_path)
    assert path.exists()
    assert path.name == "My_Thread.md"
    assert "Hi" in path.read_text()
