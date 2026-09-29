#!/usr/bin/env python3
"""Re-authorize with the full set of scopes (gmail+drive+calendar+sheets+docs).

Reuses the client_id/client_secret/token_uri from the existing credential
file, runs a local OAuth flow on localhost:8000, and writes the new
(refresh_token-preserving) credential back to the same file.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gw_common import ALL_SCOPES, add_common_args, cred_path  # noqa: E402

REDIRECT_PORT = 8000


def main():
    ap = argparse.ArgumentParser(description="Re-authorize Google scopes")
    add_common_args(ap)
    ap.add_argument("--port", type=int, default=REDIRECT_PORT)
    args = ap.parse_args()

    path = cred_path(args.user)
    if not path.exists():
        sys.exit(f"Credential file not found: {path}")
    old = json.loads(path.read_text())

    from google_auth_oauthlib.flow import InstalledAppFlow
    import oauthlib.oauth2.rfc6749.parameters as _params

    # Google returns the union of previously granted scopes when
    # include_granted_scopes=true; oauthlib raises on that scope change.
    _orig_validate = _params.validate_token_parameters
    _params.validate_token_parameters = lambda *a, **k: None
    client_config = {
        "installed": {
            "client_id": old["client_id"],
            "client_secret": old["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": old.get("token_uri", "https://oauth2.googleapis.com/token"),
            "redirect_uris": [f"http://localhost:{args.port}/"],
        }
    }
    try:
        flow = InstalledAppFlow.from_client_config(client_config, ALL_SCOPES)
        creds = flow.run_local_server(
            port=args.port,
            open_browser=False,
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
    finally:
        _params.validate_token_parameters = _orig_validate
    path.write_text(creds.to_json())
    print(f"Credentials updated for {args.user}; scopes now cover all services.")


if __name__ == "__main__":
    main()
