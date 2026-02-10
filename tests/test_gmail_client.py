"""Unit tests for gmail_client. Mocks only the Gmail API request."""

import base64
from unittest.mock import MagicMock

from gmail_exporter.gmail_client import get_message_parts, get_thread_messages


def _b64(s: str) -> str:
    """Encode string as base64url (Gmail format)."""
    return base64.urlsafe_b64encode(s.encode()).decode()


# --- get_message_parts ---


def test_get_message_parts_single_html():
    payload = {
        "mimeType": "text/html",
        "body": {"data": _b64("<p>Hello</p>")},
    }
    out = get_message_parts(payload)
    assert out["text/html"] == "<p>Hello</p>"
    assert out["text/plain"] is None


def test_get_message_parts_single_plain():
    payload = {
        "mimeType": "text/plain",
        "body": {"data": _b64("Plain text")},
    }
    out = get_message_parts(payload)
    assert out["text/plain"] == "Plain text"
    assert out["text/html"] is None


def test_get_message_parts_multipart_alternative():
    payload = {
        "parts": [
            {"mimeType": "text/plain", "body": {"data": _b64("Plain")}},
            {"mimeType": "text/html", "body": {"data": _b64("<p>HTML</p>")}},
        ]
    }
    out = get_message_parts(payload)
    assert out["text/plain"] == "Plain"
    assert out["text/html"] == "<p>HTML</p>"


def test_get_message_parts_nested_multipart():
    """multipart/mixed wrapping multipart/alternative."""
    payload = {
        "parts": [
            {
                "parts": [
                    {"mimeType": "text/plain", "body": {"data": _b64("Nested plain")}},
                    {"mimeType": "text/html", "body": {"data": _b64("<b>Nested</b>")}},
                ]
            }
        ]
    }
    out = get_message_parts(payload)
    assert out["text/plain"] == "Nested plain"
    assert out["text/html"] == "<b>Nested</b>"


# --- get_thread_messages (mocked request) ---


def test_get_thread_messages_returns_parsed_messages():
    thread_response = {
        "messages": [
            {
                "id": "msg1",
                "payload": {
                    "headers": [
                        {"name": "From", "value": "alice@test.com"},
                        {"name": "Date", "value": "Mon, 1 Jan 2024 12:00:00"},
                        {"name": "Subject", "value": "Test"},
                    ],
                    "mimeType": "text/html",
                    "body": {"data": _b64("<p>Hello</p>")},
                },
            }
        ]
    }

    mock_execute = MagicMock(return_value=thread_response)
    mock_get = MagicMock(return_value=MagicMock(execute=mock_execute))
    mock_threads = MagicMock(get=mock_get)
    mock_users = MagicMock(threads=MagicMock(return_value=mock_threads))
    service = MagicMock(users=MagicMock(return_value=mock_users))

    result = get_thread_messages(service, "thread-123")

    assert len(result) == 1
    msg = result[0]
    assert msg.id == "msg1"
    assert msg.headers.from_addr == "alice@test.com"
    assert msg.headers.date == "Mon, 1 Jan 2024 12:00:00"
    assert msg.headers.subject == "Test"
    assert msg.html == "<p>Hello</p>"
    assert msg.plain is None

    mock_get.assert_called_once_with(userId="me", id="thread-123", format="full")


def test_get_thread_messages_empty_thread():
    mock_execute = MagicMock(return_value={"messages": []})
    mock_get = MagicMock(return_value=MagicMock(execute=mock_execute))
    service = MagicMock(
        users=MagicMock(return_value=MagicMock(threads=MagicMock(get=mock_get)))
    )

    result = get_thread_messages(service, "empty")

    assert result == []
