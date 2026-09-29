# google-workspace-api

直接调用 Google Workspace REST API 的脚本集合（不经过 MCP），覆盖 Gmail / Google Drive / Google Calendar / Google Sheets / Google Docs 五个服务。可作为 Kimi Code 等 Agent 的 skill 使用，也可单独作为 CLI 工具使用。

**[English README](README.en.md)**

## 特性

- **零配置运行**：通过 `uv run --with ...` 自动拉起依赖，无需手动建虚拟环境
- **OAuth token 自动刷新**：access token 过期时自动用 refresh_token 刷新并写回凭据文件
- **多账号支持**：`--user` 参数或 `GMAIL_USER` 环境变量切换账号
- **智能导出**：Google 文档/表格/PPT 在下载时自动导出为 txt/csv

## 安装与凭据

1. 克隆本仓库：
   ```bash
   git clone https://github.com/MatroshkaLJY/google-workspace-api-skill.git
   cd google-workspace-api-skill
   ```

2. 准备 OAuth 凭据文件，保存到 `~/.google_workspace_mcp/credentials/<账号>.json`
   （Google Cloud Console 下载的 desktop OAuth client 授权 JSON，含 refresh_token）。
   **切勿将该文件提交到任何仓库。**

3. （可选）作为 Kimi Code skill 使用：
   ```bash
   mkdir -p ~/.kimi-code/skills/google-workspace-api
   cp SKILL.md ~/.kimi-code/skills/google-workspace-api/
   cp -r scripts ~/.kimi-code/skills/google-workspace-api/
   ```

## 快速上手

```bash
export http_proxy=http://127.0.0.1:7897 https_proxy=http://127.0.0.1:7897  # 如需要代理
S=scripts

# 发邮件
uv run --with google-api-python-client --with google-auth-httplib2 --with google-auth --with httplib2 \
  python $S/gmail.py send --to someone@example.com --subject "标题" --body "正文"

# 列日程
uv run ... python $S/gcal.py list

# 读表格
uv run ... python $S/sheets.py read <spreadsheet_id> "Sheet1!A1:D10"
```

完整命令清单见 [SKILL.md](SKILL.md)。

## 重新授权

凭据 scope 不足或 refresh_token 失效时：

```bash
uv run --with google-api-python-client --with google-auth-httplib2 --with google-auth \
  --with google-auth-oauthlib --with httplib2 \
  python scripts/auth.py
```

脚本会打印授权 URL。Desktop OAuth 客户端的 redirect 是 `http://localhost:8000`，如果机器没有浏览器，可通过 SSH 隧道在本机浏览器完成授权。

## 前提条件

- Google Cloud 项目需启用 Gmail / Calendar / Drive / Sheets / Docs API
- 能访问 `googleapis.com`（直连或代理）

## 安全说明

- 仓库中不包含任何凭据；凭据只存放在 `~/.google_workspace_mcp/credentials/` 本地目录
- `.gitignore` 已排除 `__pycache__/`、凭据和 token 文件
- 运行脚本时请勿打印凭据文件内容
