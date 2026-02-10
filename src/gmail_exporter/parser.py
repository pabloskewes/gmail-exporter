"""HTML/plain cleaning: remove quoted content, preserve code blocks."""

from bs4 import BeautifulSoup

from gmail_exporter.types import Message, RawMessage


def clean_html_content(html: str) -> str:
    """Remove Gmail quote blocks (.gmail_quote). Preserve pre/code."""
    if not html or not html.strip():
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for quote in soup.find_all(class_="gmail_quote"):
        quote.decompose()
    for elem in soup.find_all("blockquote"):
        if "gmail_quote" in (elem.get("class") or []):
            elem.decompose()
    return str(soup)


def _clean_plain_quotes(text: str) -> str:
    """Remove quoted content from plain text."""
    if not text or not text.strip():
        return ""
    lines = text.split("\n")
    clean_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("On ") and "wrote:" in stripped.lower():
            break
        if stripped == ">":
            break
        if line.startswith(">"):
            continue
        clean_lines.append(line)
    return "\n".join(clean_lines).strip()


def extract_message(raw: RawMessage) -> Message:
    """Convert RawMessage to cleaned Message."""
    body_html = ""
    body_plain = _clean_plain_quotes(raw.plain or "")

    if raw.html:
        body_html = clean_html_content(raw.html)
    elif raw.plain:
        body_plain = _clean_plain_quotes(raw.plain)

    return Message(
        from_addr=raw.headers.from_addr,
        date=raw.headers.date,
        subject=raw.headers.subject,
        body_html=body_html,
        body_plain=body_plain,
    )
