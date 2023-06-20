import asyncio
import os

import dotenv
import httpx
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp

dotenv.load_dotenv()

user_chat_ids: dict[str, str] = {}

slack = AsyncApp(token=os.getenv("SLACK_BOT_TOKEN"))
client = httpx.AsyncClient(base_url=os.getenv("API_BASE_URL"), timeout=60)


async def start_chat() -> tuple[str, str]:
    response = await client.post("/start-chat")
    json = response.json()
    return json["chat_id"], json["message"]


async def send_message(chat_id: str, user_message: str) -> list[str]:
    async with httpx.AsyncClient(base_url=os.getenv("API_BASE_URL")) as client:
        response = await client.post(
            "/send-message", json={"chat_id": chat_id, "user_message": user_message}
        )
    json = response.json()
    return json["messages"]


@slack.command("/start-chat")
async def on_start(ack, body, respond):
    await ack()

    chat_id, answer = await start_chat()
    user_chat_ids[body["user_id"]] = chat_id

    await respond(answer)


@slack.event("message")
async def on_message(message, say):
    user_id = message["user"]

    if user_id not in user_chat_ids:
        await say("Start a chat with the `/start-chat` command.")
        return

    answer, score_message = await send_message(user_chat_ids[user_id], message["text"])

    if score_message is not None:
        await say(score_message)

    await say(answer)


async def main():
    await AsyncSocketModeHandler(slack, os.getenv("SLACK_APP_TOKEN")).start_async()


if __name__ == "__main__":
    asyncio.run(main())