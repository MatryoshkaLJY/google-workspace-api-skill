---
name: google-workspace-api
description: 直接调用 Google Workspace API（Gmail/Drive/Calendar/Sheets/Docs），不经过 MCP。当用户要求收发邮件、管理云盘文件、查看/创建日程、读写表格或文档时使用。授权已完成，凭据缓存在 ~/.google_workspace_mcp/credentials/。
---

# Google Workspace Direct API

不使用 MCP，直接通过 Google REST API 操作。OAuth 授权已完成，
凭据文件：`~/.google_workspace_mcp/credentials/frozemin@gmail.com.json`
（不要打印或泄露其内容，脚本只负责加载；token 过期自动刷新写回）。

## 运行方式

```bash
export http_proxy=http://127.0.0.1:7897 https_proxy=http://127.0.0.1:7897
DEPS="--with google-api-python-client --with google-auth-httplib2 --with google-auth --with httplib2"
S=~/.kimi-code/skills/google-workspace-api/scripts
alias gw="uv run \$DEPS python"   # 实际使用时直接展开写
```

脚本列表（均在 `$S/` 下）：

- `gmail.py` — `profile` / `send --to --subject --body [--attach f..]` /
  `list [--query] [--max]` / `search --query` / `read <id>`
- `drive.py` — `list [--query] [--max]` / `download <file_id> <out>` /
  `upload <path> [--name] [--folder_id]` / `mkdir <name> [--parent_id]` /
  `share <file_id> --email X [--role reader|writer]`
  （Google 文档/表格/PPT 自动 export 为 txt/csv）
- `gcal.py` — `list [--calendar primary] [--start "2026-01-01 00:00"] [--end] [--max]` /
  `create --summary S [--start "YYYY-MM-DD HH:MM"] [--end] [--description]` /
  `delete <event_id>`
  （时间默认 Asia/Shanghai，缺省会议时长 1 小时）
- `sheets.py` — `read <ss_id> <range>` / `append|update <ss_id> <range> --values "a,b;1,2"` /
  `create --title T`（`;` 分行，`,` 分列）
- `docs.py` — `create --title T [--text 初始内容]` / `read <doc_id> [--limit]`

公共参数：`--user` 可切换账号（默认 frozemin@gmail.com，或环境变量 GMAIL_USER）。

示例（发邮件）：
```bash
uv run --with google-api-python-client --with google-auth-httplib2 --with google-auth --with httplib2 \
  python ~/.kimi-code/skills/google-workspace-api/scripts/gmail.py \
  send --to frozemin@gmail.com --subject "标题" --body "正文"
```

## 重新授权

凭据 scope 不足或 refresh_token 失效时，运行：
```bash
uv run --with google-api-python-client --with google-auth-httplib2 --with google-auth \
  --with google-auth-oauthlib --with httplib2 \
  python ~/.kimi-code/skills/google-workspace-api/scripts/auth.py
```
会打印一个授权 URL，需在本机浏览器或用隧道打开：
`ssh -N -p 95 -L 8000:localhost:8000 matryoshka@202.120.39.112`
（Desktop OAuth 客户端，redirect 为 http://localhost:8000，局域网 IP 会被 Google 拒绝）

## 前提

- GCP 项目（gcpaiassistant, 263248647554）需启用对应 API：
  Gmail / Google Calendar / Drive / Sheets / Docs。
- 代理环境变量需指向可用代理（或直连能访问 googleapis.com）。
