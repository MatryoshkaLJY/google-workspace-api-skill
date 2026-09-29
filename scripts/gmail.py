#!/usr/bin/env python3
"""Direct Gmail API helper (no MCP). Uses cached OAuth credentials."""
import argparse
import base64
import sys
from email.message import EmailMessage
from pathlib import Path as FsPath

sys.path.insert(0, str(FsPath(__file__).parent))
from gw_common import add_common_args, get_service  # noqa: E402


def fmt_headers(h):
    return f"[{h.get('date','')}] From: {h.get('from','')} | To: {h.get('to','')} | Subject: {h.get('subject','')}"


def cmd_send(svc, args):
    msg = EmailMessage()
    msg["To"] = args.to
    msg["From"] = args.user
    msg["Subject"] = args.subject
    msg.set_content(args.body)
    for f in args.attach or []:
        data = FsPath(f).read_bytes()
        msg.add_attachment(
            data, maintype="application", subtype="octet-stream",
            filename=FsPath(f).name,
        )
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    sent = svc.users().messages().send(
        userId="me", body={"raw": raw}).execute()
    print("sent_message_id:", sent.get("id"))


def cmd_list(svc, args):
    res = svc.users().messages().list(
        userId="me", q=args.query, maxResults=args.max).execute()
    ids = [m["id"] for m in res.get("messages", [])]
    if not ids:
        print("(no messages)")
        return
    for mid in ids:
        meta = svc.users().messages().get(
            userId="me", id=mid, format="metadata").execute()
        print(meta["id"], fmt_headers(meta["payload"]["headers"]))


def cmd_read(svc, args):
    m = svc.users().messages().get(
        userId="me", id=args.id, format="full").execute()
    print(fmt_headers(m["payload"]["headers"]))
    print("---")

    def walk(part):
        if part.get("mimeType") == "text/plain" and "body" in part:
            data = part["body"].get("data")
            if data:
                return base64.urlsafe_b64decode(
                    data.replace("-", "+").replace("_", "/")).decode(
                    "utf-8", "replace")
        return "".join(walk(p) for p in part.get("parts", []))

    print(walk(m["payload"])[: args.limit])


def cmd_profile(svc, args):
    p = svc.users().getProfile(userId="me").execute()
    print("email:", p.get("emailAddress"))
    print("historyId:", p.get("historyId"))


def main():
    ap = argparse.ArgumentParser(description="Direct Gmail API helper")
    add_common_args(ap)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("send")
    sp.add_argument("--to", required=True)
    sp.add_argument("--subject", required=True)
    sp.add_argument("--body", required=True)
    sp.add_argument("--attach", nargs="*", default=None)

    sp = sub.add_parser("list")
    sp.add_argument("--query", default="in:inbox")
    sp.add_argument("--max", type=int, default=10)

    sp = sub.add_parser("search")
    sp.add_argument("--query", required=True)
    sp.add_argument("--max", type=int, default=10)

    sp = sub.add_parser("read")
    sp.add_argument("id")
    sp.add_argument("--limit", type=int, default=5000)

    sub.add_parser("profile")

    args = ap.parse_args()
    svc = get_service("gmail", args.user)
    try:
        {"send": cmd_send, "list": cmd_list, "search": cmd_list,
         "read": cmd_read, "profile": cmd_profile}[args.cmd](svc, args)
    finally:
        svc.close()


if __name__ == "__main__":
    main()
