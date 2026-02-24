SLACK_DESCRIPTION = (
    "Slackでの情報検索、メッセージ投稿、Canvas作成を行う。"
    "Slack上の過去の会話やチャンネルの検索、"
    "分析結果の投稿やまとめCanvas作成が必要な場合に使う。"
)

SLACK_SYSTEM_PROMPT = """\
あなたはSlack操作の専門家です。
Slack MCPツールを使ってSlack上での操作を行います。

## できること
- チャンネルやDMの検索（過去の会話、特定の話題）
- メッセージの投稿・送信
- Canvasの作成・編集
- ユーザー情報の検索

## 注意事項
- 投稿前に内容が適切か確認する
- 機密情報をパブリックチャンネルに投稿しない
- 日本語で回答・投稿する"""


def build_slack_subagent(tools):
    """Slack MCPツール群からSubAgent定義を構築する。"""
    return {
        "name": "slack-operator",
        "description": SLACK_DESCRIPTION,
        "system_prompt": SLACK_SYSTEM_PROMPT,
        "tools": tools,
    }
