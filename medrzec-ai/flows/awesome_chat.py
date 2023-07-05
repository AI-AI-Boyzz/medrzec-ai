from langchain.chat_models import ChatOpenAI

from .. import FlowEnum
from .flow import Flow, FlowResponse


class AwesomeChat(Flow):
    def __init__(self) -> None:
        self.llm = ChatOpenAI(temperature=1, model="gpt-4", client=None)

    async def start_conversation(self) -> FlowResponse[str]:
        response = await self.llm.apredict(
            "Tell the user how awesome they are and how much you like them."
            " Use Markdown formatting. Add emojis."
        )
        return FlowResponse(
            response, flow_suggestions=[FlowEnum.AWESOME.as_suggestion()]
        )

    async def submit_message(self, _: str) -> FlowResponse[list[str]]:
        raise NotImplementedError()
