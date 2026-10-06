# Privacy Policy

Effective date: October 6, 2026

Google Workspace API Skill is an open-source, locally run command-line tool. It does not operate a hosted service or send your Google Workspace data to the project maintainer.

## Data the tool accesses

After you authorize it, the tool may access the Google Workspace data needed for commands you run, including:

- Gmail messages and account profile information
- Google Drive files, folders, and permissions
- Google Calendar events
- Google Sheets spreadsheets
- Google Docs documents

The tool also uses OAuth credentials, including access and refresh tokens, to authenticate requests to Google.

## How data is used

Data is used only to perform the command you request, such as reading or sending email, listing or transferring files, managing calendar events, or reading and editing documents and spreadsheets. Google user data is handled in accordance with the [Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy), including its Limited Use requirements.

## Storage and retention

OAuth credentials are stored locally in `~/.google_workspace_mcp/credentials/`. Data returned by Google is printed locally or written to a path you choose. The project maintainer does not receive or retain this data. Local credentials and exported data remain until you delete them.

## Sharing

The tool sends requests directly between your computer and Google APIs. It does not sell, share, or transfer Google user data to the project maintainer, advertisers, data brokers, or other third parties. Google processes requests under its own privacy policy.

## Security

Keep credential files private and do not commit them to source control. The repository excludes common credential paths and token files, but you are responsible for securing the device and environment where the tool runs.

## Your choices

You can stop using the tool, delete local credentials and downloaded data, or revoke its access from your [Google Account permissions](https://myaccount.google.com/permissions) at any time.

## Changes

Material changes to this policy will be published in this file with a new effective date.

## Contact

For privacy questions, open an issue in the [project repository](https://github.com/MatryoshkaLJY/google-workspace-api-skill/issues).
