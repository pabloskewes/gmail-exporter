"""OAuth2 authentication for Gmail API.

Handles credential loading, token persistence, and automatic token refresh.
Uses credentials.json (from Google Cloud Console) and persists token.json
to avoid re-authentication on each run.
"""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_gmail_service(
    credentials_path: str | Path | None = None, token_path: str | Path | None = None
) -> Resource:
    """Create and return an authenticated Gmail API service.

    Looks for token.json in the working directory. If not found or expired,
    runs OAuth2 flow via browser and persists new token.
    """
    credentials_path = Path(credentials_path or CREDENTIALS_FILE)
    token_path = Path(token_path or TOKEN_FILE)

    if not credentials_path.exists():
        raise FileNotFoundError(
            f"Credentials file not found: {credentials_path}\n"
            "Download it from Google Cloud Console and place it in the project root."
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

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)
