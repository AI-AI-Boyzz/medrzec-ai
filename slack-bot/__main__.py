import asyncio
import os

import dotenv
import httpx
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp


class RequestException(Exception):
    pass


dotenv.load_dotenv()

user_chat_ids: dict[str, str] = {}

slack = AsyncApp(token=os.getenv("SLACK_BOT_TOKEN"))
client = httpx.AsyncClient(base_url=os.getenv("API_BASE_URL"), timeout=60)


async def start_chat() -> tuple[str, str]:
    response = await client.post("/start-chat")
    json = response.json()

    if response.status_code != 200:
        raise RequestException(json["detail"])

    return json["chat_id"], json["message"]


async def send_message(chat_id: str, user_message: str) -> list[str]:
    response = await client.post(
        "/send-message", json={"chat_id": chat_id, "user_message": user_message}
    )
    json = response.json()

    if response.status_code != 200:
        raise RequestException(json["detail"])

    return json["messages"]


@slack.command("/start-chat")
async def on_start(ack, body, respond):
    await ack()

    try:
        chat_id, answer = await start_chat()
    except RequestException as e:
        await respond(str(e))
        return

    user_chat_ids[body["user_id"]] = chat_id

    await respond(answer)


@slack.event("message")
async def on_message(message, say):
    user_id = message["user"]

    if user_id not in user_chat_ids:
        await say("Start a chat with the `/start-chat` command.")
        return

    try:
        messages = await send_message(user_chat_ids[user_id], message["text"])
    except RequestException as e:
        await say(str(e))
        return

    for message in messages:
        await say(message)


async def main():
    await AsyncSocketModeHandler(slack, os.getenv("SLACK_APP_TOKEN")).start_async()


if __name__ == "__main__":
    asyncio.run(main())
