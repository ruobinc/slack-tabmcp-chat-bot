import re
from services.reply import send_reply_with_loading
from services.thread_history import fetch_thread_context


async def handle_mention(event, client):
    """チャンネルやスレッドでの@メンションに対してスレッドで返信する。"""
    user_text = re.sub(r"<@[A-Z0-9]+>\s*", "", event.get("text", "")).strip()
    thread_ts = event.get("thread_ts", event["ts"])
    channel = event["channel"]

    thread_context = await fetch_thread_context(client, channel, thread_ts)

    await send_reply_with_loading(
        text=user_text,
        thread_id=thread_ts,
        channel=channel,
        thread_ts=thread_ts,
        client=client,
        thread_context=thread_context,
    )
