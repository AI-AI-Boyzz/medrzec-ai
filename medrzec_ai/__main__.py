import asyncio
import base64
import contextlib
import hmac
import os
import secrets
from asyncio import Lock
from typing import Annotated
from uuid import uuid4

import dotenv
import httpx
import sqlalchemy.exc
import stripe
import stripe.error
from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from . import FlowEnum
from .database import Database, User
from .flows.awesome_chat import AwesomeChat
from .flows.flow import Flow, FlowResponse, FlowSuggestion
from .flows.question_and_playbook_chat import QuestionAndPlaybookChat
from .flows.remote_work_score import TeamRoles
from .flows.remote_work_score_and_playbook import RemoteWorkScoreAndPlaybookChat
from .flows.remote_work_score_intro import RemoteWorkScoreIntroChat
from .utils import api_utils
from .utils.text_utils import EmojiReplacer, TextFormat

dotenv.load_dotenv()

active_conversations: dict[str, tuple[Flow, Lock]] = {}

db = Database()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])
stripe.api_key = os.environ["STRIPE_API_KEY"]
client = httpx.AsyncClient()
emoji_replacer = EmojiReplacer()

asyncio.get_event_loop().create_task(emoji_replacer.load_emojis(client))


class FlowSuggestionsResponse(BaseModel):
    flow_suggestions: list[FlowSuggestion]


class StartChatResponse(BaseModel):
    chat_id: str
    message: str
    flow_suggestions: list[FlowSuggestion] | None
    is_paid: bool


class SendMessageResponse(BaseModel):
    messages: list[str]
    flow_suggestions: list[FlowSuggestion] | None


class AddUserRequest(BaseModel):
    api_key: str
    email: str
    country: str
    industry: str
    profession: str


class DeleteUserRequest(BaseModel):
    api_key: str
    email: str


class StripeWebhookRequest(BaseModel):
    type: str
    data: dict[str, str]


async def start_chat(
    flow: FlowEnum, text_format: TextFormat
) -> tuple[str, FlowResponse]:
    match flow:
        case FlowEnum.QUESTIONS_AND_PLAYBOOK:
            chat = QuestionAndPlaybookChat(text_format)
        case FlowEnum.REMOTE_WORK_SCORE_INTRO:
            chat = RemoteWorkScoreIntroChat()
        case FlowEnum.REMOTE_WORK_SCORE_TEAM_MEMBER:
            chat = RemoteWorkScoreAndPlaybookChat(TeamRoles.TEAM_MEMBER, text_format)
        case FlowEnum.REMOTE_WORK_SCORE_PEOPLE_LEADER:
            chat = RemoteWorkScoreAndPlaybookChat(TeamRoles.PEOPLE_LEADER, text_format)
        case FlowEnum.AWESOME:
            chat = AwesomeChat()

    chat_id = uuid4().hex
    response = await chat.start_conversation()
    response.response = emoji_replacer.replace_emojis(response.response)

    if response.flow_suggestions is None:
        active_conversations[chat_id] = (chat, asyncio.Lock())

    return (chat_id, response)


async def user_message(conversation_id: str, message: str) -> FlowResponse:
    if conversation_id not in active_conversations:
        raise HTTPException(404, "This chat doesn't exist.")

    chat, lock = active_conversations[conversation_id]

    if lock.locked():
        raise HTTPException(429, "Please wait for the previous answer.")

    async with lock:
        response = await chat.submit_message(message)
        response.response = list(map(emoji_replacer.replace_emojis, response.response))

        if response.flow_suggestions is not None:
            del active_conversations[conversation_id]

    return response


@app.get("/", response_class=Response)
async def index():
    return


@app.get("/flow-suggestions", response_model=FlowSuggestionsResponse)
async def flow_suggestions():
    return FlowSuggestionsResponse(
        flow_suggestions=[
            FlowEnum.REMOTE_WORK_SCORE_INTRO.as_suggestion(),
            FlowEnum.QUESTIONS_AND_PLAYBOOK.as_suggestion(),
        ]
    )


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

        user = None

    else:
        raise HTTPException(401, "Missing credentials.")

    if user is not None:
        purchases = db.get_purchases(user.id)
        is_paid = bool(purchases)
    else:
        is_paid = False

    (chat_id, response) = await start_chat(flow, text_format)
    return StartChatResponse(
        chat_id=chat_id,
        message=emoji_replacer.replace_emojis(response.response),
        flow_suggestions=response.flow_suggestions,
        is_paid=is_paid,
    )


@app.delete("/chats/{chat_id}")
async def delete_conversation(chat_id: str):
    try:
        del active_conversations[chat_id]
    except KeyError as e:
        raise HTTPException(404, "This chat doesn't exist.") from e


@app.post("/chats/{chat_id}/messages", response_model=SendMessageResponse)
async def send_message(chat_id: str, content: str):
    api_utils.limit_input_len(content)
    response = await user_message(chat_id, content)
    return SendMessageResponse(
        messages=response.response,
        flow_suggestions=response.flow_suggestions,
    )


@app.post("/users", response_class=Response)
async def new_user(request: AddUserRequest):
    if not check_service_key(request.api_key):
        raise HTTPException(401, "Invalid API key.")

    with contextlib.suppress(sqlalchemy.exc.IntegrityError):
        db.add_user(
            User(
                email=request.email,
                country=request.country,
                industry=request.industry,
                profession=request.profession,
            )
        )


@app.delete("/users", response_class=Response)
async def delete_user(request: DeleteUserRequest):
    if not check_service_key(request.api_key):
        raise HTTPException(401, "Invalid API key.")

    with contextlib.suppress(sqlalchemy.exc.IntegrityError):
        db.delete_user(request.email)


@app.get("/checkout-session")
async def create_checkout(user_token: str):
    token = await fetch_token(user_token)
    email = token["email"]

    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                "price": "remote-how-ai-production",
                "quantity": 1,
            },
        ],
        mode="payment",
        success_url=os.environ["STRIPE_REDIRECT_URL"],
        customer_email=email,
    )

    return RedirectResponse(checkout_session.url)


@app.post("/stripe-webhooks")
async def stripe_webhook(request: Request, stripe_signature: Annotated[str, Header()]):
    try:
        event = stripe.Webhook.construct_event(
            await request.body(), stripe_signature, os.environ["STRIPE_WEBHOOK_SECRET"]
        )
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(400, "Invalid signature.") from e

    if event.type != "checkout.session.completed":
        return Response(status_code=204)

    user = db.get_user(event.data.object.customer_details.email)

    if user is None:
        raise HTTPException(404, "User not found.")

    db.add_purchase(user.id)

    return Response(status_code=204)


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
