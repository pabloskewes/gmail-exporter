"""HTML/plain cleaning: remove quoted content, preserve code blocks."""

from bs4 import BeautifulSoup

from gmail_exporter.types import Message, RawMessage


def clean_html_content(html: str) -> str:
    """Remove full thread history (last blockquote in each gmail_quote div). Preserve contextual quotes."""
    if not html or not html.strip():
        return ""
    soup = BeautifulSoup(html, "html.parser")
    
    # For each gmail_quote div, remove only the last blockquote (full history)
    for quote_div in soup.find_all("div", class_="gmail_quote"):
        blockquotes = quote_div.find_all("blockquote", class_="gmail_quote", recursive=False)
        if blockquotes:
            blockquotes[-1].decompose()
        
        # Also remove attribution lines ("El jue, ... escribió:")
        for attr_div in quote_div.find_all("div", class_="gmail_attr"):
            attr_div.decompose()
    
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
        attachments=raw.attachments,
    )
