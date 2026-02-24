import asyncio
import logging
import os
import signal

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from handlers.mention import handle_mention
from handlers.dm import handle_dm
from services.agent import init_agent, shutdown_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = App(token=os.environ["SLACK_BOT_TOKEN"])

app.event("app_mention")(handle_mention)
app.event("message")(handle_dm)


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # MCPクライアント + DeepAgent を起動時に初期化
    logger.info("Agent初期化中...")
    loop.run_until_complete(init_agent())
    logger.info("Agent初期化完了")

    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])

    def _shutdown(signum, frame):
        logger.info("シャットダウン中...")
        handler.close()
        loop.run_until_complete(shutdown_agent())
        loop.close()

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    handler.start()


if __name__ == "__main__":
    main()
