# Herokuデプロイ手順

## 前提

- Heroku CLIインストール済み
- `heroku login --sso` でログイン済み
- Dockerインストール済み

## 初回デプロイ

```bash
# アプリ作成
heroku apps:create slack-tabmcp-chat-bot

# スタックをcontainerに設定
heroku stack:set container

# 環境変数設定（.envからHerokuに一括反映）
heroku plugins:install heroku-config  # 初回のみ
heroku config:push --overwrite

# Container Registryにログイン＆デプロイ
heroku container:login
heroku container:push worker
heroku container:release worker

# workerプロセス起動
heroku ps:scale worker=1
```

## 環境変数の更新

```bash
# .envを編集後、Herokuに反映
heroku config:push --overwrite

# Herokuの現在の設定を.envにバックアップ
heroku config:pull --overwrite
```

## 更新デプロイ

```bash
heroku container:push worker && heroku container:release worker
```

## 確認コマンド

```bash
# ログ確認
heroku logs --tail

# プロセス状態確認
heroku ps

# 環境変数確認
heroku config
```

## 注意事項

- `ANTHROPIC_API_KEY`を設定しないこと（空でも設定されると`langchain-aws`がAPIキーを優先してしまう）
- `heroku config:push`は`.env`の全変数を反映するため、ローカル専用の変数は`config:unset`で除外する
- Socket Modeのためworkerプロセスとしてデプロイ（webではない）
- `uv.lock`の更新後は必ずコミットしてからデプロイ
- ローカルでDocker起動する場合、Heroku workerと競合するため`heroku ps:scale worker=0`で停止する
