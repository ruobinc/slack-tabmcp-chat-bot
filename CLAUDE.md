# Slack TabMCP Chat Bot

Slack Bolt for Python (AsyncApp) + Socket ModeのChatBot。Dockerコンテナ化し、Heroku Container Registryでデプロイ。

## 技術スタック

- Python 3.12 / Slack Bolt (AsyncApp) / Socket Mode
- LLM: LangChain DeepAgent + ChatBedrockConverse (AWS Bedrock Claude)
- SubAgent: Tableau MCP (Stdio) / Slack MCP (HTTP) / Web検索 (Tavily)
- MCP統合: langchain-mcp-adapters (MultiServerMCPClient)
- 会話管理: LangGraph InMemorySaver（スレッドごとにコンテキスト維持）
- パッケージ管理: uv
- コンテナ: Docker (Python 3.12 + Node.js 22 + Tableau MCP)
- デプロイ: Heroku Container Registry (workerプロセス)

## 開発コマンド

- `uv add <pkg>` - パッケージ追加
- `uv lock` - lockfile再生成（Python版変更時は必須）
- `docker compose up --build` - ローカルDocker起動
- `export $(cat .env | grep -v '^#' | grep -v '^$' | xargs) && uv run python app.py` - ローカル直接起動
- `export $(cat .env | grep -v '^#' | grep -v '^$' | xargs) && uv run python test_local.py "クエリ"` - Slack抜きローカルテスト

## デプロイ

- `heroku container:login && heroku container:push worker && heroku container:release worker` - Herokuコンテナデプロイ
- `heroku ps:scale worker=1` - worker起動
- `heroku logs --tail` - ログ確認
- 詳細: docs/heroku-deploy.md

## 注意事項

- `.python-version`とpyproject.tomlの`requires-python`のバージョンを一致させること
- `uv lock`後は必ずuv.lockをコミットしてからデプロイ
- Container Registry使用時はDockerfileのCMDが使われる（Procfileはフォールバック用に残す）
- ローカル起動時、Heroku上でworkerが稼働中だとSocket Modeの接続が競合する。テスト時は`heroku ps:scale worker=0`で停止するか、Herokuにデプロイして確認する
- `ANTHROPIC_API_KEY`とAWS認証が両方あると`langchain-aws`はAPIキーを優先する
- Herokuへの環境変数設定時、`.env`の値が空だと空文字が設定される。`heroku config`で確認すること

## コード構成

```
app.py              # エントリーポイント（AsyncApp初期化 + ハンドラー登録 + 起動）
Dockerfile          # Dockerイメージ定義（Python 3.12 + Node.js 22 + Tableau MCP）
docker-compose.yml  # ローカル開発用Docker Compose
.dockerignore       # Dockerビルド除外設定
handlers/           # イベントハンドラー（mention.py, dm.py）
services/           # ビジネスロジック
├── agent.py        # DeepAgentシングルトン管理・invoke
├── mcp_client.py   # MultiServerMCPClientシングルトン（Tableau Stdio + Slack HTTP）
├── subagents/      # SubAgent定義（tableau.py, slack_agent.py, web.py）
└── reply.py        # ローディングUX・LLM応答フォーマット・Slack送信
test_local.py       # Slack抜きローカルテスト（.gitignore）
docs/plans/         # 設計・実装計画ドキュメント
```

## MCP統合の注意事項

- `MultiServerMCPClient`はコンテキストマネージャー非対応（v0.1.0+）。`get_tools()`を直接呼ぶ
- `get_tools(server_name=...)`はキーワード引数のみ（位置引数不可）
- Tableau MCP direct-trust: 環境変数は`CONNECTED_APP_SECRET_ID`
- Slack MCP: `mcp.slack.com/mcp` + User Token (xoxp-) が必須。
- Slack MCPの`headers`設定で`Authorization: Bearer {token}`を渡す

## イベントハンドリング

- `app.event("app_mention")` → チャンネル/スレッドのメンション。`thread_ts`でスレッド返信
- `app.event("message")` → DM処理。`channel_type == "im"`でフィルタ、`bot_id`チェックで自己応答防止
- AsyncApp使用のため、ハンドラーとclient呼び出しは全て`async/await`が必要
- 新しいイベント追加時はSlack API管理画面でEvent Subscriptionsとスコープも更新すること
