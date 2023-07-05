from .. import FlowEnum
from .flow import Flow, FlowResponse


class RemoteWorkScoreIntroChat(Flow):
    async def start_conversation(self) -> FlowResponse[str]:
        return FlowResponse(
            "Please select your role in the team",
            flow_suggestions=[
                FlowEnum.REMOTE_WORK_SCORE_TEAM_MEMBER.as_suggestion(),
                FlowEnum.REMOTE_WORK_SCORE_PEOPLE_LEADER.as_suggestion(),
            ],
        )

    async def submit_message(self, _: str) -> FlowResponse[list[str]]:
        raise NotImplementedError()
