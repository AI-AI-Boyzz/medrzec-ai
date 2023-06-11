import os
import re

import dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from .playbook_chat import PlaybookChat
from .question_chat import QuestionChat

dotenv.load_dotenv()

active_conversations: dict[str, QuestionChat | PlaybookChat] = {}

app = App(token=os.getenv("SLACK_BOT_TOKEN"))


@app.command("/start")
def on_start(ack, body, respond):
    ack()

    chat = QuestionChat()
    active_conversations[body["user_id"]] = chat
    respond(chat.start_conversation())


@app.event("message")
def on_message(message, say):
    user_id = message["user"]
    chat = active_conversations.get(user_id)

    if chat is None:
        say("Start a chat with the /start command.")
        return

    answer = chat.submit_message(message["text"])

    if match := re.search(r"Score: (\d+)", answer, re.IGNORECASE):
        user_score = match[1]
        say(f"Done, your score is {user_score}%!")

        chat = PlaybookChat()
        active_conversations[user_id] = chat
        say(chat.start_conversation(user_score))
        return

    say(answer)


if __name__ == "__main__":
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()
