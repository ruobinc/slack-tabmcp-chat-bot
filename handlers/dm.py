from services.reply import send_reply_with_loading


def handle_dm(event, client):
    """BotへのDMに返信する。Bot自身のメッセージは無視する。"""
    if event.get("bot_id"):
        return
    if event.get("channel_type") != "im":
        return

    user_text = event.get("text", "").strip()
    channel = event["channel"]
    thread_ts = event.get("thread_ts", event["ts"])

    send_reply_with_loading(
        text=user_text,
        thread_id=thread_ts,
        channel=channel,
        thread_ts=thread_ts,
        client=client,
    )
