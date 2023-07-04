import re

from .. import TextFormat
from .flow import Flow
from .playbook_chat import PlaybookChat
from .question_chat import QuestionChat

PLAYBOOK_URL = "https://remotehow.notion.site/Remote-Work-Playbook-Template-b537fb9b503f4a0a9296774d464777d6"
PLAYBOOK_UPSELL = (
    "Get access to the world’s best playbook on #remotework, and improve your score."
)


class QuestionAndPlaybookChat(Flow):
    def __init__(self, text_format: TextFormat) -> None:
        super().__init__()

        self.text_format = text_format

        self.flow: Flow = QuestionChat()

    async def start_conversation(self) -> str:
        return await self.flow.start_conversation()

    async def submit_message(self, text: str) -> list[str]:
        answer = (await self.flow.submit_message(text))[0]

        if match := re.search(r"Score: (\d+)", answer, re.IGNORECASE):
            user_score = int(match[1])

            score_message = score_to_message(user_score, self.text_format)

            self.flow = PlaybookChat(user_score)
            answer = await self.flow.start_conversation()

        else:
            score_message = None

        messages = [answer]

        if score_message is not None:
            messages.insert(0, score_message)

        return messages


def score_to_message(score: int, text_format: TextFormat) -> str:
    match text_format:
        case TextFormat.MARKDOWN:
            bold = "**"
            paragraph = "\n\n"
            playbook = f"[{PLAYBOOK_UPSELL}]({PLAYBOOK_URL})"
        case TextFormat.SLACK:
            bold = "*"
            paragraph = "\n"
            playbook = f"<{PLAYBOOK_URL}|{PLAYBOOK_UPSELL}>"

    playbook += f"{paragraph}Let’s dive in 🚀"

    message = f"{bold}Your Remote Work Score is {score}%!{bold} "

    if score > 90:
        message += """🧠
You are a REMOTE PRO — super well done! ⭐⭐⭐ Keep rocking!"""

    elif score > 50:
        message += f"""👏👏👏
You are familiar with remote work but need more guidance to feel fully comfortable in it. Let us help you! 🏗️
{playbook}"""

    else:
        message += f"""😅
You need more assistance with remote work to feel fully comfortable in it. Let us help you! 🏗️
{playbook}"""
    return message.replace("\n", paragraph)
