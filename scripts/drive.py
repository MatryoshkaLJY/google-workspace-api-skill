#!/usr/bin/env python3
"""Direct Google Drive API helper."""
import argparse
import io
import sys
from pathlib import Path as FsPath

sys.path.insert(0, str(FsPath(__file__).parent))
from gw_common import add_common_args, get_service  # noqa: E402

EXPORT_MIME = {
    "application/vnd.google-apps.document": ("text/plain", ".txt"),
    "application/vnd.google-apps.spreadsheet": ("text/csv", ".csv"),
    "application/vnd.google-apps.presentation": ("text/plain", ".txt"),
}


def cmd_list(svc, args):
    res = svc.files().list(
        q=args.query, pageSize=args.max,
        fields="files(id,name,mimeType,modifiedTime,webViewLink)",
        orderBy="modifiedTime desc").execute()
    files = res.get("files", [])
    if not files:
        print("(no files)")
        return
    for f in files:
        print(f"{f['id']}  {f['modifiedTime'][:10]}  {f['mimeType']}  {f['name']}")
        print(f"    {f.get('webViewLink','')}")


def cmd_download(svc, args):
    meta = svc.files().get(fileId=args.file_id, fields="name,mimeType").execute()
    out = FsPath(args.out_path)
    if out.is_dir() or str(args.out_path).endswith("/"):
        ext = EXPORT_MIME.get(meta["mimeType"], (None, ""))[1]
        out = out / (meta["name"] + ext)
    if meta["mimeType"] in EXPORT_MIME:
        target, _ = EXPORT_MIME[meta["mimeType"]]
        data = svc.files().export(fileId=args.file_id, mimeType=target).execute()
        out.write_bytes(data)
    else:
        data = svc.files().get_media(fileId=args.file_id).execute()
        out.write_bytes(data)
    print("saved:", out)


def cmd_upload(svc, args):
    from googleapiclient.http import MediaFileUpload

    p = FsPath(args.local_path)
    media = MediaFileUpload(str(p), resumable=True)
    body = {"name": args.name or p.name}
    if args.folder_id:
        body["parents"] = [args.folder_id]
    f = svc.files().create(body=body, media_body=media,
                           fields="id,name,webViewLink").execute()
    print(f["id"], f["name"])
    print(f.get("webViewLink", ""))


def cmd_mkdir(svc, args):
    body = {"name": args.name, "mimeType": "application/vnd.google-apps.folder"}
    if args.parent_id:
        body["parents"] = [args.parent_id]
    f = svc.files().create(body=body, fields="id,name,webViewLink").execute()
    print(f["id"], f["name"])


def cmd_share(svc, args):
    svc.permissions().create(
        fileId=args.file_id,
        body={"type": "user", "role": args.role, "emailAddress": args.email},
        sendNotificationEmail=True).execute()
    print("shared:", args.file_id, "->", args.email, "as", args.role)


def main():
    ap = argparse.ArgumentParser(description="Direct Drive API helper")
    add_common_args(ap)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list")
    sp.add_argument("--query")
    sp.add_argument("--max", type=int, default=10)

    sp = sub.add_parser("download")
    sp.add_argument("file_id")
    sp.add_argument("out_path")

    sp = sub.add_parser("upload")
    sp.add_argument("local_path")
    sp.add_argument("--name")
    sp.add_argument("--folder_id")

    sp = sub.add_parser("mkdir")
    sp.add_argument("name")
    sp.add_argument("--parent_id")

    sp = sub.add_parser("share")
    sp.add_argument("file_id")
    sp.add_argument("--email", required=True)
    sp.add_argument("--role", choices=["reader", "commenter", "writer"], default="reader")

    args = ap.parse_args()
    svc = get_service("drive", args.user)
    try:
        {"list": cmd_list, "download": cmd_download, "upload": cmd_upload,
         "mkdir": cmd_mkdir, "share": cmd_share}[args.cmd](svc, args)
    finally:
        svc.close()


if __name__ == "__main__":
    main()
