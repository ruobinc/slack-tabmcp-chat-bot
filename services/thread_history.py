import logging
import re

logger = logging.getLogger(__name__)

HISTORY_LIMIT = 10


async def fetch_thread_context(client, channel: str, thread_ts: str) -> str:
    """Slackスレッドの直近メッセージを取得し、コンテキスト文字列を返す。

    履歴が1件以下（自分のメッセージのみ）の場合は空文字を返す。
    """
    try:
        result = await client.conversations_replies(
            channel=channel, ts=thread_ts, limit=HISTORY_LIMIT + 1,
        )
        messages = result.get("messages", [])
    except Exception:
        logger.exception("スレッド履歴の取得に失敗")
        return ""

    # 最後のメッセージ（トリガーとなった発言）を除外
    history = messages[:-1] if len(messages) > 1 else []
    if not history:
        return ""

    lines = []
    for msg in history:
        user = msg.get("user", "不明")
        text = msg.get("text", "")
        # メンション記法を読みやすく変換
        text = re.sub(r"<@[A-Z0-9]+>", "@user", text)
        if msg.get("bot_id"):
            lines.append(f"Bot: {text}")
        else:
            lines.append(f"<@{user}>: {text}")

    formatted = "\n".join(lines)
    return (
        "以下はSlackスレッドの会話履歴です：\n"
        "---\n"
        f"{formatted}\n"
        "---\n\n"
        "上記の会話を踏まえて回答してください。\n\n"
    )
