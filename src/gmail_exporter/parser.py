"""HTML parsing and cleaning for Gmail messages.

Removes redundant quoted content (.gmail_quote) that Gmail adds to each reply.
Preserves <pre> and <code> blocks for proper code formatting in Markdown.
"""

from __future__ import annotations

from bs4 import BeautifulSoup


def clean_html_content(html_string: str) -> str:
    """Remove Gmail quote blocks from HTML while preserving code blocks.

    Gmail embeds the entire previous conversation in each reply inside
    elements with class 'gmail_quote'. Removing these eliminates redundant
    content. BeautifulSoup preserves <pre> and <code> tags; markdownify
    will later convert them to fenced code blocks.
    """
    if not html_string or not html_string.strip():
        return ""

    soup = BeautifulSoup(html_string, "html.parser")

    # Remove Gmail quote blocks (the key step to avoid infinite repetition)
    for quote in soup.find_all(class_="gmail_quote"):
        quote.decompose()

    # Also remove blockquotes that may contain gmail_quote in class
    for elem in soup.find_all("blockquote"):
        classes = elem.get("class") or []
        if "gmail_quote" in classes:
            elem.decompose()

    return str(soup)


def _clean_plain_text_quotes(text: str) -> str:
    """Remove common quoted content markers from plain text."""
    if not text or not text.strip():
        return ""

    lines = text.split("\n")
    clean_lines: list[str] = []
    for line in lines:
        # Stop at "On ... wrote:" style quote headers
        if line.strip().startswith("On ") and "wrote:" in line.lower():
            break
        # Stop at lines that are just ">" (quote marker)
        if line.strip() == ">":
            break
        # Skip lines that are purely quoted (start with >)
        if line.startswith(">"):
            continue
        clean_lines.append(line)

    return "\n".join(clean_lines).strip()


def extract_message_data(message: dict) -> dict[str, str]:
    """Extract and clean message data for Markdown export.

    message: dict with keys headers, html, plain (from gmail_client)
    Returns dict with: from, date, subject, body_html, body_plain
    body_html is cleaned HTML (prefer this for conversion).
    body_plain is cleaned plain text (fallback when no HTML).
    """
    headers = message.get("headers", {})
    from_addr = headers.get("From", "")
    date = headers.get("Date", "")
    subject = headers.get("Subject", "")

    html = message.get("html")
    plain = message.get("plain", "")

    body_html = ""
    body_plain = _clean_plain_text_quotes(plain) if plain else ""

    if html:
        body_html = clean_html_content(html)
    elif plain:
        # Use plain text as fallback; no HTML to clean
        body_html = ""  # Writer will use body_plain
        body_plain = _clean_plain_text_quotes(plain)

    return {
        "from": from_addr,
        "date": date,
        "subject": subject,
        "body_html": body_html,
        "body_plain": body_plain,
    }
