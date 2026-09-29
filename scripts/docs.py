#!/usr/bin/env python3
"""Direct Google Docs API helper."""
import argparse
import sys
from pathlib import Path as FsPath

sys.path.insert(0, str(FsPath(__file__).parent))
from gw_common import add_common_args, get_service  # noqa: E402


def doc_text(doc):
    out = []

    def walk(el):
        if "paragraph" in el.get("paragraph", {}):
            pass
        for seg in el.get("paragraph", {}).get("elements", []):
            out.append(seg.get("textRun", {}).get("content", ""))
        for t in el.get("table", {}).get("tableRows", []):
            for cell in t.get("tableCells", []):
                for c in cell.get("content", []):
                    walk(c)

    for el in doc.get("body", {}).get("content", []):
        walk(el)
    return "".join(out)


def cmd_create(svc, args):
    doc = svc.documents().create(body={"title": args.title}).execute()
    doc_id = doc["documentId"]
    print(doc_id)
    if args.text:
        svc.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": [{"insertText": {
                "location": {"index": 1}, "text": args.text}}]}).execute()
    print("https://docs.google.com/document/d/" + doc_id + "/edit")


def cmd_read(svc, args):
    doc = svc.documents().get(documentId=args.doc_id).execute()
    print("title:", doc.get("title"))
    print("---")
    print(doc_text(doc)[: args.limit])


def main():
    ap = argparse.ArgumentParser(description="Direct Docs API helper")
    add_common_args(ap)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("create")
    sp.add_argument("--title", required=True)
    sp.add_argument("--text")

    sp = sub.add_parser("read")
    sp.add_argument("doc_id")
    sp.add_argument("--limit", type=int, default=10000)

    args = ap.parse_args()
    svc = get_service("docs", args.user)
    try:
        {"create": cmd_create, "read": cmd_read}[args.cmd](svc, args)
    finally:
        svc.close()


if __name__ == "__main__":
    main()
