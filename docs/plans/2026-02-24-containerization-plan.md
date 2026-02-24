# コンテナ化 実装計画

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Slack TabMCP ChatBotをDocker化し、Heroku Container Registryでデプロイ可能にする

**Architecture:** Python 3.12 + Node.js 22のシングルステージイメージ。Tableau MCPをコンテナ内でgit clone＆ビルドし、Stdio接続を維持。ローカルはdocker-compose、本番はHeroku Container Registry。

**Tech Stack:** Docker, docker-compose, Heroku Container Registry, uv, Node.js 22

---

### Task 1: .dockerignore作成

**Files:**
- Create: `.dockerignore`

**Step 1: .dockerignoreを作成**

```
.env
.env.example
.git
.gitignore
__pycache__
*.pyc
.venv
node_modules
test_local.py
docs/
tasks/
.claude/
CLAUDE.md
README.md
```

**Step 2: コミット**

```bash
git add .dockerignore
git commit -m ".dockerignoreを作成"
```

---

### Task 2: Dockerfile作成

**Files:**
- Create: `Dockerfile`
- 参考: `/Users/ruobin.chang/Documents/Develop/tabmcp-extensions/Dockerfile`

**Step 1: Dockerfileを作成**

```dockerfile
FROM python:3.12-bookworm

# システムツール
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Node.js 22 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Tableau MCP サーバービルド
RUN git clone https://github.com/tableau/tableau-mcp.git /opt/tableau-mcp \
    && cd /opt/tableau-mcp \
    && npm ci && npm run build

# アプリケーション依存関係
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# アプリケーションコード
COPY . .

# 環境変数
ENV TABLEAU_MCP_PATH=/opt/tableau-mcp/build/index.js

CMD ["uv", "run", "python", "app.py"]
```

**Step 2: Dockerイメージをビルドして検証**

```bash
docker build -t slack-tabmcp-bot .
```

Expected: ビルド成功。エラーなし。

**Step 3: コンテナ内の構成を確認**

```bash
docker run --rm slack-tabmcp-bot ls /opt/tableau-mcp/build/index.js
docker run --rm slack-tabmcp-bot node --version
docker run --rm slack-tabmcp-bot python --version
docker run --rm slack-tabmcp-bot uv --version
```

Expected: 各コマンドが正常に出力される。

**Step 4: コミット**

```bash
git add Dockerfile
git commit -m "Dockerfileを作成"
```

---

### Task 3: docker-compose.yml作成

**Files:**
- Create: `docker-compose.yml`

**Step 1: docker-compose.ymlを作成**

```yaml
services:
  bot:
    build:
      context: .
      dockerfile: Dockerfile
    env_file:
      - .env
    environment:
      - TABLEAU_MCP_PATH=/opt/tableau-mcp/build/index.js
    volumes:
      - .:/app:cached
      - uv-cache:/root/.cache/uv
    command: uv run python app.py

volumes:
  uv-cache:
```

**Step 2: docker-compose upで起動テスト**

```bash
docker compose up --build
```

Expected: ビルド成功＆Socket Mode接続開始のログが出力される。
注意: Heroku workerが稼働中の場合は先に `heroku ps:scale worker=0` で停止すること。

**Step 3: Ctrl+Cで停止後、コミット**

```bash
git add docker-compose.yml
git commit -m "docker-compose.ymlを作成"
```

---

### Task 4: Herokuデプロイ＆Slackテスト

**Files:**
- 変更なし（Heroku CLI操作のみ）

**Step 1: 既存workerを停止**

```bash
heroku ps:scale worker=0
```

**Step 2: Container Registryにログイン＆プッシュ**

```bash
heroku container:login
heroku container:push worker
```

Expected: Dockerイメージがビルドされ、Heroku Registryにプッシュされる。

**Step 3: リリース**

```bash
heroku container:release worker
```

**Step 4: workerを起動**

```bash
heroku ps:scale worker=1
```

**Step 5: ログを確認**

```bash
heroku logs --tail
```

Expected: Socket Mode接続成功のログ。エラーなし。

**Step 6: Slackでテスト**

- ボットにメンションして応答を確認
- DMを送って応答を確認
- Tableau関連の質問をしてMCP Stdio接続が機能することを確認

---

### Task 5: CLAUDE.mdとドキュメント更新

**Files:**
- Modify: `CLAUDE.md` - デプロイコマンド更新
- Modify: `docs/heroku-deploy.md` - Container Registry手順追記

**Step 1: CLAUDE.mdのデプロイセクションを更新**

Container Registryコマンドを追加:
```
- `docker compose up --build` - ローカルDocker起動
- `heroku container:login && heroku container:push worker && heroku container:release worker` - Herokuコンテナデプロイ
```

**Step 2: コミット**

```bash
git add CLAUDE.md docs/heroku-deploy.md
git commit -m "コンテナ化のドキュメントを更新"
```
