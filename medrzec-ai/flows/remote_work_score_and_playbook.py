from .. import TextFormat
from .flow import Flow, FlowResponse
from .playbook_chat import PlaybookChat
from .remote_work_score import RemoteWorkScoreChat, TeamRoles


class RemoteWorkScoreAndPlaybookChat(Flow):
    def __init__(self, role: TeamRoles, text_format: TextFormat) -> None:
        self.text_format = text_format

        self.flow: Flow = RemoteWorkScoreChat(role, text_format)

    async def start_conversation(self) -> FlowResponse[str]:
        return await self.flow.start_conversation()

    async def submit_message(self, text: str) -> FlowResponse[list[str]]:
        response = await self.flow.submit_message(text)
        messages = response.response

        if response.flow_suggestions is not None:
            self.flow = PlaybookChat(response.extra["remote_work_score"])
            messages.append((await self.flow.start_conversation()).response)

        return FlowResponse(messages)
