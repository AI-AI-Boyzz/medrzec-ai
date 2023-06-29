from langchain.chat_models import ChatOpenAI

from .flow import Flow


class AwesomeChat(Flow):
    def __init__(self) -> None:
        super().__init__()

        self.llm = ChatOpenAI(temperature=1, model="gpt-4", client=None)

    async def start_conversation(self) -> str:
        self.flow_end = True
        return await self.llm.apredict(
            "Tell the user how awesome they are and how much you like them."
            " Use Markdown formatting. Add emojis."
        )

    async def submit_message(self, _: str) -> list[str]:
        raise NotImplementedError()
