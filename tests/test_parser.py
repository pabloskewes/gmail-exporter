"""Unit tests for parser."""

from gmail_exporter.parser import clean_html_content, extract_message
from gmail_exporter.types import Headers, RawMessage


def test_clean_html_removes_gmail_quote():
    html = '<p>New</p><div class="gmail_quote"><p>Quoted</p></div>'
    out = clean_html_content(html)
    assert "New" in out
    assert "Quoted" not in out


def test_clean_html_preserves_content():
    html = "<p>Hello</p><pre><code>print(1)</code></pre>"
    out = clean_html_content(html)
    assert "Hello" in out
    assert "print(1)" in out


def test_clean_plain_quotes_via_extract():
    raw = RawMessage(
        id="x",
        headers=Headers(from_addr="a@b.com", date="Mon", subject="Test"),
        html=None,
        plain="Hi there\n\nOn Mon, 1 Jan, Bob wrote:\n\n> old quote",
    )
    msg = extract_message(raw)
    assert "Hi there" in msg.body_plain
    assert "On Mon" not in msg.body_plain
    assert "old quote" not in msg.body_plain


def test_extract_prefers_html():
    raw = RawMessage(
        id="x",
        headers=Headers(from_addr="a@b.com", date="Mon", subject="Test"),
        html="<p>HTML content</p>",
        plain="Plain content",
    )
    msg = extract_message(raw)
    assert msg.body_html == "<p>HTML content</p>"
    assert msg.from_addr == "a@b.com"
