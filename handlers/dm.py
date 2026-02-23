from services.reply import generate_reply


def handle_dm(event, say):
    """BotへのDMに返信する。Bot自身のメッセージは無視する。"""
    # Bot自身のメッセージは無視
    if event.get("bot_id"):
        return

    # DMはimチャンネルタイプのみ処理
    if event.get("channel_type") != "im":
        return

    user_text = event.get("text", "").strip()
    reply = generate_reply(user_text)
    say(text=reply)
