"""Unit tests for parser."""

from gmail_exporter.parser import clean_html_content, extract_message
from gmail_exporter.types import Headers, RawMessage


def test_clean_html_removes_last_blockquote():
    """Test that last blockquote (full history) is removed."""
    html = '''<p>New message</p>
    <div class="gmail_quote">
        <blockquote class="gmail_quote"><p>Contextual quote</p></blockquote>
        <div>Response to quote</div>
        <blockquote class="gmail_quote"><p>Full thread history</p></blockquote>
    </div>'''
    out = clean_html_content(html)
    assert "New message" in out
    assert "Contextual quote" in out  # Preserved
    assert "Response to quote" in out  # Preserved
    assert "Full thread history" not in out  # Removed (last blockquote)


def test_clean_html_removes_attribution():
    """Test that gmail_attr divs are removed."""
    html = '''<div class="gmail_quote">
        <div class="gmail_attr">On Mon, Bob wrote:</div>
        <blockquote class="gmail_quote"><p>History</p></blockquote>
    </div>'''
    out = clean_html_content(html)
    assert "On Mon, Bob wrote:" not in out
    assert "History" not in out  # Last blockquote removed


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
