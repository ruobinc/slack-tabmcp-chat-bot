SLACK_DESCRIPTION = (
    "Slackでの情報検索、メッセージ投稿、Canvas作成を行う。"
    "Slack上の過去の会話やチャンネルの検索、"
    "分析結果の投稿やまとめCanvas作成が必要な場合に使う。"
)

SLACK_SYSTEM_PROMPT = """\
あなたはSlack操作の専門家です。
Slack MCPツールでSlack上の操作を行います。

## ルール
- ツール呼び出しは最大3回以内で完了すること
- 機密情報をパブリックチャンネルに投稿しない
- 日本語で回答・投稿する"""

SLACK_ALLOWED_TOOLS = {
    "slack_search_public_and_private",
    "slack_search_channels",
    "slack_read_channel",
    "slack_read_thread",
    "slack_create_canvas",
    "slack_send_message",
}


def build_slack_subagent(tools):
    """Slack MCPツール群からSubAgent定義を構築する。"""
    filtered = [t for t in tools if t.name in SLACK_ALLOWED_TOOLS]
    return {
        "name": "slack-operator",
        "description": SLACK_DESCRIPTION,
        "system_prompt": SLACK_SYSTEM_PROMPT,
        "tools": filtered,
    }
