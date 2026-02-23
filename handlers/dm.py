from services.reply import send_reply_with_loading


def handle_dm(event, client):
    """BotへのDMに返信する。Bot自身のメッセージは無視する。"""
    if event.get("bot_id"):
        return
    if event.get("channel_type") != "im":
        return

    user_text = event.get("text", "").strip()
    channel = event["channel"]

    send_reply_with_loading(
        text=user_text,
        thread_id=channel,
        channel=channel,
        thread_ts=None,
        client=client,
    )
