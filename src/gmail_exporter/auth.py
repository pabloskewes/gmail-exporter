"""OAuth2 authentication for Gmail API.

Handles credential loading, token persistence, and automatic token refresh.
Uses ~/.config/gmail-exporter/ so the tool works from anywhere.
"""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CONFIG_DIR = Path.home() / ".config" / "gmail-exporter"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
TOKEN_FILE = CONFIG_DIR / "token.json"


def get_gmail_service(
    credentials_path: str | Path | None = None, token_path: str | Path | None = None
) -> Resource:
    """Create and return an authenticated Gmail API service.

    Default: ~/.config/gmail-exporter/credentials.json and token.json.
    """
    credentials_path = Path(credentials_path or CREDENTIALS_FILE)
    token_path = Path(token_path or TOKEN_FILE)

    if not credentials_path.exists():
        raise FileNotFoundError(
            f"Credentials file not found: {credentials_path}\n"
            f"Create {CONFIG_DIR} and place credentials.json there.\n"
            "Download from Google Cloud Console (OAuth 2.0 Desktop app)."
        )

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES
            )
            creds = flow.run_local_server(port=0)

        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)
