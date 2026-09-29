# google-workspace-api

A script collection that calls Google Workspace REST APIs directly (no MCP), covering Gmail / Google Drive / Google Calendar / Google Sheets / Google Docs. Usable as a skill for agents like Kimi Code, or standalone as CLI tools.

**[中文说明](README.md)**

## Features

- **Zero-setup runs**: dependencies are pulled automatically via `uv run --with ...`, no virtualenv needed
- **Auto token refresh**: expired access tokens are refreshed with the refresh_token and written back to the credential file
- **Multi-account**: switch accounts with `--user` or the `GMAIL_USER` environment variable
- **Smart export**: Google Docs/Sheets/Slides are exported as txt/csv on download

## Setup & Credentials

1. Clone this repo:
   ```bash
   git clone https://github.com/MatroshkaLJY/google-workspace-api-skill.git
   cd google-workspace-api-skill
   ```

2. Place your OAuth credential file at `~/.google_workspace_mcp/credentials/<account>.json`
   (a Google Cloud Console desktop OAuth client authorized-user JSON containing a refresh_token).
   **Never commit this file to any repository.**

3. (Optional) Install as a Kimi Code skill:
   ```bash
   mkdir -p ~/.kimi-code/skills/google-workspace-api
   cp SKILL.md ~/.kimi-code/skills/google-workspace-api/
   cp -r scripts ~/.kimi-code/skills/google-workspace-api/
   ```

## Quick Start

```bash
export http_proxy=http://127.0.0.1:7897 https_proxy=http://127.0.0.1:7897  # if a proxy is needed
S=scripts

# Send an email
uv run --with google-api-python-client --with google-auth-httplib2 --with google-auth --with httplib2 \
  python $S/gmail.py send --to someone@example.com --subject "Subject" --body "Body"

# List calendar events
uv run ... python $S/gcal.py list

# Read a spreadsheet
uv run ... python $S/sheets.py read <spreadsheet_id> "Sheet1!A1:D10"
```

See [SKILL.md](SKILL.md) for the full command reference.

## Re-authorization

When credential scopes are insufficient or the refresh_token is invalid:

```bash
uv run --with google-api-python-client --with google-auth-httplib2 --with google-auth \
  --with google-auth-oauthlib --with httplib2 \
  python scripts/auth.py
```

The script prints an authorization URL. Desktop OAuth clients redirect to `http://localhost:8000`; if the machine has no browser, complete authorization through an SSH tunnel from a local browser.

## Prerequisites

- Google Cloud project with Gmail / Calendar / Drive / Sheets / Docs APIs enabled
- Network access to `googleapis.com` (direct or via proxy)

## Security Notes

- This repository contains no credentials; they live only in `~/.google_workspace_mcp/credentials/` locally
- `.gitignore` excludes `__pycache__/`, credential and token files
- Never print the contents of credential files when running the scripts
