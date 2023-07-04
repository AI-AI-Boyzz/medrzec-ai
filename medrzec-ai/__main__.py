import asyncio
import base64
import contextlib
import hmac
import os
import secrets
from asyncio import Lock
from uuid import uuid4

import dotenv
import httpx
import sqlalchemy.exc
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import FlowEnum, TextFormat
from .database import Database, User
from .flows.awesome_chat import AwesomeChat
from .flows.flow import Flow
from .flows.question_and_playbook_chat import QuestionAndPlaybookChat
from .flows.remote_work_score import RemoteWorkScoreChat

dotenv.load_dotenv()

active_conversations: dict[str, tuple[Flow, Lock]] = {}

db = Database()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])
client = httpx.AsyncClient()


class StartChatResponse(BaseModel):
    chat_id: str
    message: str
    flow_end: bool


class SendMessageResponse(BaseModel):
    messages: list[str]
    flow_end: bool


class ModifyUser(BaseModel):
    api_key: str
    email: str


async def start_chat(flow: FlowEnum, text_format: TextFormat) -> tuple[str, str, bool]:
    match flow:
        case FlowEnum.QUESTIONS_AND_PLAYBOOK:
            chat = QuestionAndPlaybookChat(text_format)
        case FlowEnum.REMOTE_WORK_SCORE:
            chat = RemoteWorkScoreChat()
        case FlowEnum.AWESOME:
            chat = AwesomeChat()

    chat_id = uuid4().hex
    answer = await chat.start_conversation()
    flow_end = chat.flow_end

    if not flow_end:
        active_conversations[chat_id] = (chat, asyncio.Lock())

    return (chat_id, answer, flow_end)


async def user_message(conversation_id: str, message: str) -> tuple[list[str], bool]:
    if conversation_id not in active_conversations:
        raise HTTPException(404, "This chat doesn't exist.")

    chat, lock = active_conversations[conversation_id]

    if lock.locked():
        raise HTTPException(429, "Please wait for the previous answer.")

    async with lock:
        messages = await chat.submit_message(message)
        flow_end = chat.flow_end

        if flow_end:
            del active_conversations[conversation_id]

    return (messages, flow_end)


@app.get("/", response_class=Response)
async def index():
    return


@app.post("/chats", response_model=StartChatResponse)
async def start_conversation(
    flow: FlowEnum,
    id_token: str | None = None,
    api_key: str | None = None,
    text_format: TextFormat = TextFormat.MARKDOWN,
):
    if id_token is not None:
        token_info = await fetch_token(id_token)
        user = db.get_user(token_info["email"])

        if user is None:
            raise HTTPException(
                401,
                "Your email is not approved yet. "
                "Contact community@remote-first.institute to get access.",
            )

    elif api_key is not None:
        if not check_service_key(api_key):
            raise HTTPException(401, "Invalid API key.")

    else:
        raise HTTPException(401, "Missing credentials.")

    (chat_id, answer, flow_end) = await start_chat(flow, text_format)
    return StartChatResponse(chat_id=chat_id, message=answer, flow_end=flow_end)


@app.delete("/chats/{chat_id}")
async def delete_conversation(chat_id: str):
    try:
        del active_conversations[chat_id]
    except KeyError as e:
        raise HTTPException(404, "This chat doesn't exist.") from e


@app.post("/chats/{chat_id}/messages", response_model=SendMessageResponse)
async def send_message(chat_id: str, content: str):
    (messages, flow_end) = await user_message(chat_id, content)
    return SendMessageResponse(messages=messages, flow_end=flow_end)


@app.post("/users", response_class=Response)
async def new_user(request: ModifyUser):
    if not check_service_key(request.api_key):
        raise HTTPException(401, "Invalid API key.")

    with contextlib.suppress(sqlalchemy.exc.IntegrityError):
        db.add_user(User(email=request.email))


@app.delete("/users", response_class=Response)
async def delete_user(request: ModifyUser):
    if not check_service_key(request.api_key):
        raise HTTPException(401, "Invalid API key.")

    with contextlib.suppress(sqlalchemy.exc.IntegrityError):
        db.delete_user(request.email)


@app.get("/slack")
async def slack(code: str):
    response = await client.post(
        "https://slack.com/api/oauth.v2.access",
        params={
            "client_id": os.environ["SLACK_CLIENT_ID"],
            "client_secret": os.environ["SLACK_CLIENT_SECRET"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": os.environ["SLACK_REDIRECT_URI"],
        },
    )

    json = response.json()

    if not json["ok"]:
        return HTTPException(400, f"OAuth error: {json['error']}")

    return f"Authorized with the {json['team']['name']} workspace."


async def fetch_token(id_token: str) -> dict:
    response = await client.get(
        "https://oauth2.googleapis.com/tokeninfo", params={"id_token": id_token}
    )

    token_info = response.json()

    if response.status_code != 200:
        raise HTTPException(400, f"OAuth error: {token_info['error']}")

    if token_info["aud"] != os.environ["GOOGLE_CLIENT_ID"]:
        raise HTTPException(400, "Invalid OAuth token.")

    if not token_info["email_verified"]:
        raise HTTPException(403, "Email not verified.")

    return token_info


def check_service_key(key: str) -> bool:
    return hmac.compare_digest(key, os.environ["SERVICE_KEY"])


def generate_api_key() -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(48)).decode()
