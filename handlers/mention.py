import re
from services.reply import send_reply_with_loading


def handle_mention(event, client):
    """チャンネルやスレッドでの@メンションに対してスレッドで返信する。"""
    user_text = re.sub(r"<@[A-Z0-9]+>\s*", "", event.get("text", "")).strip()
    thread_ts = event.get("thread_ts", event["ts"])
    channel = event["channel"]

    send_reply_with_loading(
        text=user_text,
        thread_id=thread_ts,
        channel=channel,
        thread_ts=thread_ts,
        client=client,
    )
