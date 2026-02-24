# コンテナ化設計

## 概要

Slack TabMCP ChatBotをDockerコンテナ化し、Heroku Container Registryでデプロイする。

## アプローチ

シングルステージビルド。Python 3.12 + Node.js 22 + Tableau MCPを1つのイメージに統合。

## Dockerfile

- ベース: `python:3.12-bookworm`
- Node.js 22 LTS（Tableau MCP Stdio実行用）
- uv（Pythonパッケージマネージャ）
- Tableau MCP: `github.com/tableau/tableau-mcp.git` をクローン＆ビルド → `/opt/tableau-mcp/`
- `ENV TABLEAU_MCP_PATH=/opt/tableau-mcp/build/index.js`
- `uv sync --frozen --no-dev` で依存関係インストール
- `CMD ["uv", "run", "python", "app.py"]`

## docker-compose.yml（ローカル開発用）

- `.env` ファイル読み込み
- `TABLEAU_MCP_PATH` を環境変数で上書き
- ソースコードをボリュームマウント（ホットリロード）
- ポート公開不要（Socket Modeはアウトバウンド接続）

## Herokuデプロイ

- Container Registry方式: `heroku container:push worker` → `container:release worker`
- Procfileは互換性のため残すが、Container RegistryではDockerfileのCMDが優先
- 環境変数は `heroku config:set` の既存設定をそのまま利用
- `TABLEAU_MCP_PATH` はDockerfile内のENVで固定

## .dockerignore

```
.env
.git
__pycache__
*.pyc
.venv
node_modules
test_local.py
docs/
```

## mcp_client.py の変更

`TABLEAU_MCP_PATH` は既に環境変数から読んでいるため、コード変更は不要。コンテナ内では `ENV` で `/opt/tableau-mcp/build/index.js` が設定される。
