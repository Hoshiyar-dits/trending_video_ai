
"""One-time YouTube login. Run `python -m app.modules.jobs.services.youtube_auth` and approve access in the browser."""
from pathlib import Path

from app.config import YOUTUBE_CLIENT_SECRETS, YOUTUBE_TOKEN_FILE

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def load_credentials():
    """Return saved credentials, refreshing them if expired, or None if login is needed."""
    from google.auth.exceptions import RefreshError
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    token_path = Path(YOUTUBE_TOKEN_FILE)
    if not token_path.exists():
        return None
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds.valid:
        return creds
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except RefreshError:
            return None
        token_path.write_text(creds.to_json())
        return creds
    return None


def main():
    from google_auth_oauthlib.flow import InstalledAppFlow

    if not Path(YOUTUBE_CLIENT_SECRETS).exists():
        raise SystemExit(f"OAuth client file not found: {YOUTUBE_CLIENT_SECRETS}")
    flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CLIENT_SECRETS, SCOPES)
    # access_type=offline + consent gives a refresh token, so this only has to run once.
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    Path(YOUTUBE_TOKEN_FILE).write_text(creds.to_json())
    print(f"Saved YouTube credentials to {YOUTUBE_TOKEN_FILE}")


if __name__ == "__main__":
    main()
