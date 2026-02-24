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
