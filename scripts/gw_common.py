#!/usr/bin/env python3
"""Shared helpers for direct Google Workspace API access (no MCP)."""
import os
import sys
from pathlib import Path

CRED_DIR = Path.home() / ".google_workspace_mcp" / "credentials"
DEFAULT_USER = "frozemin@gmail.com"
TIMEOUT = 30

SCOPES = {
    "gmail": ["https://www.googleapis.com/auth/gmail.modify"],
    "drive": ["https://www.googleapis.com/auth/drive"],
    "calendar": ["https://www.googleapis.com/auth/calendar"],
    "sheets": ["https://www.googleapis.com/auth/spreadsheets"],
    "docs": ["https://www.googleapis.com/auth/documents"],
}
ALL_SCOPES = [s for scopes in SCOPES.values() for s in scopes]

API_VERSIONS = {
    "gmail": ("gmail", "v1"),
    "drive": ("drive", "v3"),
    "calendar": ("calendar", "v3"),
    "sheets": ("sheets", "v4"),
    "docs": ("docs", "v1"),
}


class NeedsReauth(Exception):
    pass


def cred_path(user_email: str) -> Path:
    return CRED_DIR / f"{user_email}.json"


def load_creds(user_email: str, service: str):
    """Load cached OAuth creds; refresh if expired. Exits with hint if
    the stored scopes don't cover the requested service."""
    from google.oauth2.credentials import Credentials
    import google.auth.transport.requests as gar

    path = cred_path(user_email)
    if not path.exists():
        sys.exit(f"Credential file not found: {path}")
    need = set(SCOPES[service])
    stored = set()
    try:
        import json

        stored = set(json.loads(path.read_text()).get("scopes", []))
    except Exception:
        pass
    if not need.issubset(stored):
        missing = need - stored
        sys.exit(
            "Stored credential is missing scopes:\n  "
            + "\n  ".join(sorted(missing))
            + "\nRun re-authorization first:\n"
            + f"  python {Path(__file__).with_name('auth.py')} --user {user_email}"
        )
    creds = Credentials.from_authorized_user_file(str(path), sorted(need | stored))
    if creds.expired and creds.refresh_token:
        creds.refresh(gar.Request())
        path.write_text(creds.to_json())
    return creds


def build_service(creds, service: str):
    import google_auth_httplib2
    from googleapiclient.discovery import build
    import httplib2

    http = httplib2.Http(
        timeout=TIMEOUT,
        proxy_info=httplib2.proxy_info_from_environment(),
    )
    authorized = google_auth_httplib2.AuthorizedHttp(creds, http=http)
    api, version = API_VERSIONS[service]
    return build(api, version, http=authorized, cache_discovery=False)


def get_service(service: str, user_email: str = None):
    creds = load_creds(user_email or os.environ.get("GMAIL_USER", DEFAULT_USER), service)
    return build_service(creds, service)


def add_common_args(ap, default_user=DEFAULT_USER):
    ap.add_argument("--user", default=os.environ.get("GMAIL_USER", default_user))
