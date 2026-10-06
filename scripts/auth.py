#!/usr/bin/env python3
"""Re-authorize with the full set of scopes (gmail+drive+calendar+sheets+docs).

Reuses the client_id/client_secret/token_uri from the existing credential
file, runs a local OAuth flow on localhost:8000, and writes the new
credential back to the same file.

The local callback handler is intentionally lenient: it accepts any
authorization `code` without checking the CSRF state parameter (single-user
local tool), always replies with a normal page (no connection reset), and
trades the code for tokens afterwards.
"""
import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).parent))
from gw_common import ALL_SCOPES, add_common_args, cred_path  # noqa: E402

REDIRECT_PORT = 8000

RESULT = {}


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        if "code" in q:
            RESULT["code"] = q["code"][0]
            body = b"Authorization received. You can close this tab."
        elif "error" in q:
            RESULT["error"] = q["error"][0]
            body = ("Authorization failed: " + q["error"][0]).encode()
        else:
            body = b"Waiting for authorization..."
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


class _Server(HTTPServer):
    allow_reuse_address = True


def main():
    ap = argparse.ArgumentParser(description="Re-authorize Google scopes")
    add_common_args(ap)
    ap.add_argument("--port", type=int, default=REDIRECT_PORT)
    args = ap.parse_args()

    path = cred_path(args.user)
    if not path.exists():
        sys.exit(f"Credential file not found: {path}")
    old = json.loads(path.read_text())
    token_uri = old.get("token_uri", "https://oauth2.googleapis.com/token")
    redirect_uri = f"http://localhost:{args.port}/"

    client_config = {
        "installed": {
            "client_id": old["client_id"],
            "client_secret": old["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": token_uri,
            "redirect_uris": [redirect_uri],
        }
    }

    from google_auth_oauthlib.flow import InstalledAppFlow
    import oauthlib.oauth2.rfc6749.parameters as _params

    flow = InstalledAppFlow.from_client_config(client_config, ALL_SCOPES)
    flow.redirect_uri = redirect_uri
    # let requests_oauthlib generate and track the PKCE verifier itself
    flow.oauth2session._pkce = "S256"
    auth_url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent")
    print("Please visit this URL to authorize this application:", flush=True)
    print(auth_url, flush=True)

    server = _Server(("localhost", args.port), _Handler)
    while "code" not in RESULT and "error" not in RESULT:
        server.handle_request()
    server.server_close()
    if "error" in RESULT:
        sys.exit(f"Authorization failed: {RESULT['error']}")

    # Google returns the union of previously granted scopes when
    # include_granted_scopes=true; oauthlib raises on that scope change.
    _orig_validate = _params.validate_token_parameters
    _params.validate_token_parameters = lambda *a, **k: None
    try:
        token = flow.oauth2session.fetch_token(
            token_uri,
            code=RESULT["code"],
            client_id=old["client_id"],
            client_secret=old["client_secret"],
            include_client_id=True,
        )
    finally:
        _params.validate_token_parameters = _orig_validate
    if "access_token" not in token:
        sys.exit(f"Token exchange failed, response was: {token}")
    creds = flow.credentials
    path.write_text(creds.to_json())
    print(f"Credentials updated for {args.user}; scopes now cover all services.")


if __name__ == "__main__":
    main()
