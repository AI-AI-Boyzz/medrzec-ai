import re

from .flow import Flow
from .playbook_chat import PlaybookChat
from .question_chat import QuestionChat

PLAYBOOK_URL = "https://remotehow.notion.site/Remote-Work-Playbook-Template-b537fb9b503f4a0a9296774d464777d6"
PLAYBOOK_UPSELL = f"<{PLAYBOOK_URL}|Get access to the world’s best playbook on #remotework, and improve your score.>\nLet’s dive in 🚀"


class QuestionAndPlaybookChat(Flow):
    def __init__(self) -> None:
        self.flow: Flow = QuestionChat()

    def start_conversation(self) -> str:
        return self.flow.start_conversation()

    def submit_message(self, text: str) -> list[str]:
        answer = self.flow.submit_message(text)[0]

        if match := re.search(r"Score: (\d+)", answer, re.IGNORECASE):
            user_score = int(match[1])

            score_message = score_to_message(user_score)

            self.flow = PlaybookChat(user_score)
            answer = self.flow.start_conversation()

        else:
            score_message = None

        messages = [answer]

        if score_message is not None:
            messages.insert(0, score_message)

        return messages


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
