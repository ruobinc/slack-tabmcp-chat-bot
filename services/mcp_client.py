import os
import logging
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)

_client = None


def _build_server_config():
    """環境変数からMCPサーバー設定を構築する。"""
    servers = {}

    # Tableau MCP (Stdio) - direct-trust認証
    tableau_path = os.environ.get("TABLEAU_MCP_PATH")
    if tableau_path:
        servers["tableau"] = {
            "transport": "stdio",
            "command": "node",
            "args": [tableau_path],
            "env": {
                "TRANSPORT": "stdio",
                "AUTH": os.environ.get("TABLEAU_AUTH", "direct-trust"),
                "SERVER": os.environ.get("TABLEAU_SERVER", ""),
                "SITE_NAME": os.environ.get("TABLEAU_SITE_NAME", ""),
                "JWT_SUB_CLAIM": os.environ.get("TABLEAU_JWT_SUB_CLAIM", ""),
                "CONNECTED_APP_CLIENT_ID": os.environ.get("TABLEAU_CONNECTED_APP_CLIENT_ID", ""),
                "CONNECTED_APP_SECRET_ID": os.environ.get("TABLEAU_CONNECTED_APP_SECRET_ID", ""),
                "CONNECTED_APP_SECRET_VALUE": os.environ.get("TABLEAU_CONNECTED_APP_SECRET_VALUE", ""),
                "DEFAULT_LOG_LEVEL": "warn",
            },
        }
    else:
        logger.warning("TABLEAU_MCP_PATH未設定: Tableau SubAgentは無効")

    # Slack MCP (HTTP) - Bearer Token認証
    slack_url = os.environ.get("SLACK_MCP_SERVER")
    slack_token = os.environ.get("SLACK_MCP_USER_TOKEN")
    if slack_url and slack_token:
        servers["slack"] = {
            "transport": "streamable_http",
            "url": slack_url,
            "headers": {
                "Authorization": f"Bearer {slack_token}",
            },
        }
    elif slack_url:
        logger.warning("SLACK_MCP_USER_TOKEN未設定: Slack SubAgentは無効")
    else:
        logger.warning("SLACK_MCP_SERVER未設定: Slack SubAgentは無効")

    return servers


def get_mcp_client():
    """MultiServerMCPClientのシングルトンを返す。"""
    global _client
    if _client is not None:
        return _client
    config = _build_server_config()
    if not config:
        logger.warning("MCPサーバー設定なし: MCPクライアント未初期化")
        return None
    _client = MultiServerMCPClient(config)
    return _client
