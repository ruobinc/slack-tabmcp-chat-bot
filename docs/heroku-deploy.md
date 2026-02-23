# Herokuデプロイ手順

## 前提
- Heroku CLIインストール済み
- `heroku login --sso` でログイン済み

## 初回デプロイ

```bash
# アプリ作成
heroku apps:create slack-tabmcp-chat-bot

# 環境変数設定
heroku config:set SLACK_BOT_TOKEN=xoxb-xxx SLACK_APP_TOKEN=xapp-xxx --app slack-tabmcp-chat-bot

# デプロイ
git push heroku master

# workerプロセス起動
heroku ps:scale worker=1 --app slack-tabmcp-chat-bot
```

## 更新デプロイ

```bash
git push heroku master
```

## 確認コマンド

```bash
# ログ確認
heroku logs --tail --app slack-tabmcp-chat-bot

# プロセス状態確認
heroku ps --app slack-tabmcp-chat-bot
```

## 注意事項
- uvを使用しているため、Pythonバージョンは `.python-version` で指定する（`runtime.txt`は不可）
- Socket ModeのためProcfileは `worker`（`web`ではない）
- `.python-version` と `pyproject.toml` の `requires-python` のバージョンを一致させること
- `uv.lock` の更新後は必ずコミットしてからデプロイ
