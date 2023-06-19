import asyncio
import os
import re
from asyncio import Lock

import dotenv
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp

from .playbook_chat import PlaybookChat
from .question_chat import QuestionChat

PLAYBOOK_URL = "https://remotehow.notion.site/Remote-Work-Playbook-Template-b537fb9b503f4a0a9296774d464777d6"
PLAYBOOK_UPSELL = f"<{PLAYBOOK_URL}|Get access to the world’s best playbook on #remotework, and improve your score.>\nLet’s dive in 🚀"

dotenv.load_dotenv()

active_conversations: dict[str, tuple[QuestionChat | PlaybookChat, Lock]] = {}

app = AsyncApp(token=os.getenv("SLACK_BOT_TOKEN"))


@app.command("/start-chat")
async def on_start(ack, body, respond):
    await ack()

    lock = asyncio.Lock()
    async with lock:
        chat = QuestionChat()
        active_conversations[body["user_id"]] = (chat, lock)
        answer = await asyncio.to_thread(chat.start_conversation)

    await respond(answer)


@app.event("message")
async def on_message(message, say):
    user_id = message["user"]
    if user_id not in active_conversations:
        await say("Start a chat with the /start-chat command.")
        return

    chat, lock = active_conversations[user_id]

    if lock.locked():
        await say("Please wait for the previous answer.")
        return

    async with lock:
        answer = await asyncio.to_thread(chat.submit_message, message["text"])

        if match := re.search(r"Score: (\d+)", answer, re.IGNORECASE):
            user_score = int(match[1])
            message = f"*Your Remote Work Score is {user_score}%!* "

            if user_score > 90:
                message += """🧠
You are a REMOTE PRO — super well done! ⭐ ⭐ ⭐ Keep rocking!"""

            elif user_score > 50:
                message += f"""👏 👏 👏
You are familiar with remote work but need more guidance to feel fully comfortable in it. Let us help you! 🏗️
{PLAYBOOK_UPSELL}"""

            else:
                message += f"""😅
You need more assistance with remote work to feel fully comfortable in it. Let us help you! 🏗️
{PLAYBOOK_UPSELL}"""

            await say(message)

            chat = PlaybookChat()
            active_conversations[user_id] = (chat, lock)
            answer = await asyncio.to_thread(chat.start_conversation, user_score)

    await say(answer)


async def main():
    await AsyncSocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start_async()


if __name__ == "__main__":
    asyncio.run(main())
