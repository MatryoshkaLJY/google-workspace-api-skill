#!/usr/bin/env python3
"""Direct Google Sheets API helper."""
import argparse
import sys
from pathlib import Path as FsPath

sys.path.insert(0, str(FsPath(__file__).parent))
from gw_common import add_common_args, get_service  # noqa: E402


def parse_values(s):
    """'a,b,c;1,2,3' -> [['a','b','c'],['1','2','3']]"""
    return [[c.strip() for c in row.split(",")] for row in s.split(";")]


def cmd_read(svc, args):
    res = svc.spreadsheets().values().get(
        spreadsheetId=args.spreadsheet_id, range=args.range).execute()
    for row in res.get("values", []):
        print("\t".join(str(c) for c in row))


def cmd_append(svc, args):
    res = svc.spreadsheets().values().append(
        spreadsheetId=args.spreadsheet_id, range=args.range,
        valueInputOption="USER_ENTERED",
        body={"values": parse_values(args.values)}).execute()
    print("updated:", res.get("updates", {}).get("updatedRange", ""))


def cmd_update(svc, args):
    res = svc.spreadsheets().values().update(
        spreadsheetId=args.spreadsheet_id, range=args.range,
        valueInputOption="USER_ENTERED",
        body={"values": parse_values(args.values)}).execute()
    print("updated:", res.get("updatedRange", ""))


def cmd_create(svc, args):
    ss = svc.spreadsheets().create(
        body={"properties": {"title": args.title}},
        fields="spreadsheetId,spreadsheetUrl").execute()
    print(ss["spreadsheetId"])
    print(ss.get("spreadsheetUrl", ""))


def main():
    ap = argparse.ArgumentParser(description="Direct Sheets API helper")
    add_common_args(ap)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("read")
    sp.add_argument("spreadsheet_id")
    sp.add_argument("range")

    sp = sub.add_parser("append")
    sp.add_argument("spreadsheet_id")
    sp.add_argument("range")
    sp.add_argument("--values", required=True, help="'a,b;1,2' rows separated by ';'")

    sp = sub.add_parser("update")
    sp.add_argument("spreadsheet_id")
    sp.add_argument("range")
    sp.add_argument("--values", required=True)

    sp = sub.add_parser("create")
    sp.add_argument("--title", required=True)

    args = ap.parse_args()
    svc = get_service("sheets", args.user)
    try:
        {"read": cmd_read, "append": cmd_append, "update": cmd_update,
         "create": cmd_create}[args.cmd](svc, args)
    finally:
        svc.close()


if __name__ == "__main__":
    main()
