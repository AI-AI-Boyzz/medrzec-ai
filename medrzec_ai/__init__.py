from __future__ import annotations

from enum import StrEnum, auto

from pydantic import BaseModel


class FlowEnum(StrEnum):
    QUESTIONS_AND_PLAYBOOK = auto()
    REMOTE_WORK_SCORE_INTRO = auto()
    REMOTE_WORK_SCORE_TEAM_MEMBER = auto()
    REMOTE_WORK_SCORE_PEOPLE_LEADER = auto()
    INTERVIEW_FLOW = auto()
    AWESOME = auto()

    def as_suggestion(self) -> FlowSuggestion:
        match self:
            case FlowEnum.QUESTIONS_AND_PLAYBOOK:
                text = "Find out and help improve my Remote Work Score (legacy)"
            case FlowEnum.REMOTE_WORK_SCORE_INTRO:
                text = "Find out my Remote Work Score"
            case FlowEnum.REMOTE_WORK_SCORE_TEAM_MEMBER:
                text = "I'm a regular team member!"
            case FlowEnum.REMOTE_WORK_SCORE_PEOPLE_LEADER:
                text = "I'm a team leader!"
            case FlowEnum.AWESOME:
                text = "Tell me how awesome I am"
            case FlowEnum.INTERVIEW_FLOW:
                text = "Get my Distributed Work Score"

        return FlowSuggestion(id=self, text=text)


class FlowSuggestion(BaseModel):
    id: str
    text: str
