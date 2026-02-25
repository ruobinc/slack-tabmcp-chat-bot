import asyncio
import logging

from services.agent import invoke_agent

logger = logging.getLogger(__name__)

LOADING_MESSAGE = ":hourglass_flowing_sand: 考え中..."
SLACK_MESSAGE_LIMIT = 4000
TIMEOUT_SECONDS = 600  # 10min


async def generate_reply(text: str, thread_id: str, thread_context: str = "") -> str:
    """DeepAgentでLLM応答を生成する。90秒タイムアウト付き。"""
    try:
        return await asyncio.wait_for(
            invoke_agent(text, thread_id, thread_context=thread_context),
            timeout=TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.warning("LLM応答タイムアウト（%d秒）", TIMEOUT_SECONDS)
        return "応答がタイムアウトしました。もう一度お試しください。"
    except Exception:
        logger.exception("LLM応答生成エラー")
        return "エラーが発生しました。しばらくしてからもう一度お試しください。"


async def send_reply_with_loading(
    text: str,
    thread_id: str,
    channel: str,
    thread_ts: str,
    client,
    thread_context: str = "",
):
    """ローディングメッセージ送信→LLM応答で更新する。"""
    loading = await client.chat_postMessage(
        channel=channel,
        text=LOADING_MESSAGE,
        thread_ts=thread_ts,
    )

    reply = await generate_reply(text, thread_id, thread_context=thread_context)

    if len(reply) <= SLACK_MESSAGE_LIMIT:
        await client.chat_update(
            channel=channel,
            ts=loading["ts"],
            text=reply,
        )
    else:
        await client.chat_update(
            channel=channel,
            ts=loading["ts"],
            text=reply[:SLACK_MESSAGE_LIMIT],
        )
        for i in range(SLACK_MESSAGE_LIMIT, len(reply), SLACK_MESSAGE_LIMIT):
            await client.chat_postMessage(
                channel=channel,
                text=reply[i : i + SLACK_MESSAGE_LIMIT],
                thread_ts=thread_ts,
            )
