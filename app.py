import asyncio
import logging
import os
import signal

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from handlers.mention import handle_mention
from handlers.dm import handle_dm
from services.agent import init_agent, shutdown_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])

app.event("app_mention")(handle_mention)
app.event("message")(handle_dm)


async def main():
    # MCPクライアント + DeepAgent を起動時に初期化
    logger.info("Agent初期化中...")
    await init_agent()
    logger.info("Agent初期化完了")

    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])

    loop = asyncio.get_event_loop()

    def _shutdown(signum, frame):
        logger.info("シャットダウン中...")
        loop.create_task(_cleanup(handler))

    async def _cleanup(h):
        await h.close_async()
        await shutdown_agent()
        loop.stop()

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(main())
