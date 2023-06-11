import asyncio
import os
import re
from asyncio import Lock

import dotenv
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp

from .playbook_chat import PlaybookChat
from .question_chat import QuestionChat

PLAYBOOK_URL = "https://remotehow.notion.site/Remote-First-Work-Playbook-Template-b7a8b8437a3e4c22b68bc20e18bbd34d"

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
            message = f"Done, your score is {user_score}%! "

            if user_score > 90:
                message += """You are Fred Astaire of remote work - you know what you are doing and you act efficiently, bravo! \
🥇 See below some advice on how you can share your experience in the organization to increase the remote awareness of your colleagues. \
To their and your greater comfort of work. 🤝🏻 -> (Ideas for skills sharing)"""

            elif user_score > 50:
                message += f"""You are familiar with remote work but need clear guidance to feel comfortable in it. \
💃🏻 Let us help you! See the exercise below to improve your remote skills⬇ \
e.g. -> (some exercises for being more async and focused), what more? Use tips from this playbook to improve your score: {PLAYBOOK_URL}"""

            else:
                message += f"""Finding yourself in remote work is a challenge for you. \
Don't worry! Remote skills training and following good practices can turn your remote work nightmare into a good experience leading to a work-life balance 🧘🏻‍♂️ \
See the exercise below to improve your remote skills⬇ e.g. -> write down your typical day plan. Visualize you must cancel all the meetings - what happens? \
->do a practice of how to write messages effectively - see our recommendation on the topic (redirect to Remote Institute about it) etc. \
Use tips from this playbook to improve your score: {PLAYBOOK_URL}"""

            await say(message)

            chat = PlaybookChat()
            active_conversations[user_id] = (chat, lock)
            answer = await asyncio.to_thread(chat.start_conversation, user_score)

    await say(answer)


async def main():
    await AsyncSocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start_async()


if __name__ == "__main__":
    asyncio.run(main())
