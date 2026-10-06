#!/usr/bin/env python3
"""Direct Google Calendar API helper."""
import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path as FsPath

sys.path.insert(0, str(FsPath(__file__).parent))
from gw_common import add_common_args, get_service  # noqa: E402

TZ = timezone(timedelta(hours=8))  # Asia/Shanghai


def iso(s):
    """Accept 'YYYY-MM-DD HH:MM' or RFC3339; default TZ Asia/Shanghai."""
    if s is None:
        return None
    try:
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
    except ValueError:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=TZ)
    return dt.isoformat()


def cmd_list(svc, args):
    kw = dict(calendarId=args.calendar, maxResults=args.max,
              singleEvents=True, orderBy="startTime")
    if args.start:
        kw["timeMin"] = iso(args.start)
    if args.end:
        kw["timeMax"] = iso(args.end)
    res = svc.events().list(**kw).execute()
    for e in res.get("items", []):
        start = e["start"].get("dateTime", e["start"].get("date"))
        print(f"{e['id']}  {start}  {e.get('summary','(no title)')}")


def cmd_create(svc, args):
    start = iso(args.start) or datetime.now(TZ).replace(second=0, microsecond=0).isoformat()
    end = iso(args.end)
    if end is None:
        end = (datetime.fromisoformat(start) + timedelta(hours=1)).isoformat()
    body = {"summary": args.summary, "start": {"dateTime": start},
            "end": {"dateTime": end}}
    if args.description:
        body["description"] = args.description
    e = svc.events().insert(calendarId=args.calendar, body=body).execute()
    print(e["id"], e.get("htmlLink", ""))


def cmd_delete(svc, args):
    svc.events().delete(calendarId=args.calendar, eventId=args.event_id).execute()
    print("deleted:", args.event_id)


def main():
    ap = argparse.ArgumentParser(description="Direct Calendar API helper")
    add_common_args(ap)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list")
    sp.add_argument("--calendar", default="primary")
    sp.add_argument("--max", type=int, default=10)
    sp.add_argument("--start", help="YYYY-MM-DD HH:MM or RFC3339")
    sp.add_argument("--end")

    sp = sub.add_parser("create")
    sp.add_argument("--summary", required=True)
    sp.add_argument("--start")
    sp.add_argument("--end")
    sp.add_argument("--description")
    sp.add_argument("--calendar", default="primary")

    sp = sub.add_parser("delete")
    sp.add_argument("event_id")
    sp.add_argument("--calendar", default="primary")

    args = ap.parse_args()
    svc = get_service("calendar", args.user)
    try:
        {"list": cmd_list, "create": cmd_create, "delete": cmd_delete}[args.cmd](svc, args)
    finally:
        svc.close()


if __name__ == "__main__":
    main()
