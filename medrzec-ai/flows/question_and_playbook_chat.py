import re

from ..utils.text_utils import TextFormat
from .flow import Flow, FlowResponse
from .playbook_chat import PlaybookChat
from .question_chat import QuestionChat
from ..utils import text_utils


class QuestionAndPlaybookChat(Flow):
    def __init__(self, text_format: TextFormat) -> None:
        self.text_format = text_format

        self.flow: Flow = QuestionChat()

    async def start_conversation(self) -> FlowResponse[str]:
        return await self.flow.start_conversation()

    async def submit_message(self, text: str) -> FlowResponse[list[str]]:
        response = (await self.flow.submit_message(text)).response[0]

        if match := re.search(r"Score: (\d+)", response, re.IGNORECASE):
            user_score = int(match[1])

            score_message = text_utils.remote_work_score_message(
                user_score, self.text_format
            )

            self.flow = PlaybookChat(user_score)
            response = (await self.flow.start_conversation()).response

        else:
            score_message = None

        messages = [response]

        if score_message is not None:
            messages.insert(0, score_message)

        return FlowResponse(messages)
