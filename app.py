import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from handlers.mention import handle_mention
from handlers.dm import handle_dm

app = App(token=os.environ["SLACK_BOT_TOKEN"])

# チャンネル/スレッドでの@メンション
app.event("app_mention")(handle_mention)

# DMメッセージ
app.event("message")(handle_dm)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
