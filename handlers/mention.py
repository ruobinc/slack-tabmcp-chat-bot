import re
from services.reply import generate_reply


def handle_mention(event, say):
    """チャンネルやスレッドでの@メンションに対してスレッドで返信する。"""
    # メンション部分（<@UXXXXXX>）を除去してユーザーのメッセージを取得
    user_text = re.sub(r"<@[A-Z0-9]+>\s*", "", event.get("text", "")).strip()

    reply = generate_reply(user_text)

    # スレッド内の場合はthread_ts、そうでなければメッセージのtsをスレッドルートにする
    thread_ts = event.get("thread_ts", event["ts"])
    say(text=reply, thread_ts=thread_ts)
