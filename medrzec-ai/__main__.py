import asyncio
import os
import re
from asyncio import Lock
from uuid import uuid4

import dotenv
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .playbook_chat import PlaybookChat
from .question_chat import QuestionChat

PLAYBOOK_URL = "https://remotehow.notion.site/Remote-Work-Playbook-Template-b537fb9b503f4a0a9296774d464777d6"
PLAYBOOK_UPSELL = f"<{PLAYBOOK_URL}|Get access to the world’s best playbook on #remotework, and improve your score.>\nLet’s dive in 🚀"

dotenv.load_dotenv()

active_conversations: dict[str, tuple[QuestionChat | PlaybookChat, Lock]] = {}

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])
client = httpx.AsyncClient()


class StartChatRequest(BaseModel):
    id_token: str


class StartChatResponse(BaseModel):
    chat_id: str
    message: str
    user_name: str
    user_picture: str


class SendMessageRequest(BaseModel):
    chat_id: str
    user_message: str


class SendMessageResponse(BaseModel):
    messages: list[str]


async def start_chat(conversation_id: str) -> str:
    lock = asyncio.Lock()
    async with lock:
        chat = QuestionChat()
        active_conversations[conversation_id] = (chat, lock)
        answer = await asyncio.to_thread(chat.start_conversation)

    return answer


async def user_message(conversation_id: str, message: str) -> tuple[str, str | None]:
    if conversation_id not in active_conversations:
        raise HTTPException(404, "This conversation doesn't exist.")

    chat, lock = active_conversations[conversation_id]

    if lock.locked():
        raise HTTPException(429, "Please wait for the previous answer.")

    async with lock:
        answer = await asyncio.to_thread(chat.submit_message, message)

        if match := re.search(r"Score: (\d+)", answer, re.IGNORECASE):
            user_score = int(match[1])

            score_message = score_to_message(user_score)

            chat = PlaybookChat()
            active_conversations[conversation_id] = (chat, lock)
            answer = await asyncio.to_thread(chat.start_conversation, user_score)

        else:
            score_message = None

    return answer, score_message


@app.post("/start-chat", response_model=StartChatResponse)
async def start_conversation(request: StartChatRequest):
    response = await client.get(
        "https://oauth2.googleapis.com/tokeninfo", params={"id_token": request.id_token}
    )

    token_info = response.json()

    if response.status_code != 200:
        raise HTTPException(400, f"OAuth2 error: {token_info['error']}")

    if token_info["aud"] != os.getenv("GOOGLE_CLIENT_ID"):
        raise HTTPException(400, "Invalid OAuth2 token.")

    if not token_info["email_verified"]:
        raise HTTPException(403, "Email not verified.")

    chat_id = uuid4().hex
    answer = await start_chat(chat_id)
    return StartChatResponse(
        chat_id=chat_id,
        message=answer,
        user_name=token_info["given_name"],
        user_picture=token_info["picture"],
    )


@app.post("/send-message", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest):
    answer, score_message = await user_message(request.chat_id, request.user_message)
    messages = [answer]

    if score_message is not None:
        messages.append(score_message)

    return SendMessageResponse(messages=messages)


def score_to_message(score: int) -> str:
    message = f"*Your Remote Work Score is {score}%!* "

    if score > 90:
        message += """🧠
You are a REMOTE PRO — super well done! ⭐⭐⭐ Keep rocking!"""

    elif score > 50:
        message += f"""👏👏👏
You are familiar with remote work but need more guidance to feel fully comfortable in it. Let us help you! 🏗️
{PLAYBOOK_UPSELL}"""

    else:
        message += f"""😅
You need more assistance with remote work to feel fully comfortable in it. Let us help you! 🏗️
{PLAYBOOK_UPSELL}"""
    return message
